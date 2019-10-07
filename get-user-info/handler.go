// get-user-info

package function

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"strings"

	"github.com/pkg/errors"
)

// User contains information about a user that was returned by various services
// in the backend. For now, it all comes from the iplant-groups service.
type User struct {
	LookupURL   string `json:"-"`
	ID          string `json:"id"` // The non-UUID identifier for a user. Usually the username.
	GrouperUser string `json:"-"`
	Name        string `json:"name"` // The full name
	FirstName   string `json:"first_name"`
	LastName    string `json:"last_name"`
	Email       string `json:"email"`
	Institution string `json:"institution"`
	SourceID    string `json:"source_id"`
}

// NewUser returns a newly instantiated *User.
func NewUser(id, grouperUser, lookupURL string) *User {
	return &User{
		LookupURL:   lookupURL,
		GrouperUser: grouperUser,
		ID:          id,
	}
}

// Get populates the *User with information. Blocks and makes calls to at least
// the iplant-groups service.
func (u *User) Get() error {
	groupsURL, err := url.Parse(u.LookupURL)
	if err != nil {
		return err
	}

	q := groupsURL.Query()
	q.Set("user", u.GrouperUser)
	groupsURL.RawQuery = q.Encode()

	groupsURL.Path = fmt.Sprintf("/subjects/%s", u.ID)

	fmt.Printf("lookup URL is %s\n", groupsURL.String())

	resp, err := http.Get(groupsURL.String())
	if err != nil {
		return errors.Wrapf(err, "error getting user information for %s", u.ID)
	}

	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return errors.Wrapf(err, "error reading body for user %s", u.ID)
	}

	if resp.StatusCode < 200 || resp.StatusCode > 200 {
		return fmt.Errorf("failed user lookup (status: %s, msg %s)", resp.Status, b)
	}

	if err = json.Unmarshal(b, u); err != nil {
		return errors.Wrapf(err, "error unmarshalling user info for user %s", u.ID)
	}

	return nil
}

// ParseID returns a user's ID from their username. Right now it's basically
// anything to the left of the last @ in their username.
func ParseID(username string) string {
	hasAt := strings.Contains(username, "@")
	if !hasAt {
		return username
	}
	parts := strings.Split(username, "@")
	return strings.Join(parts[:len(parts)-1], "@")
}

// UserRequest is the structure of the request body.
type UserRequest struct {
	Username string `json:"username"`
}

// Handle is the handler for the OpenFaaS golang-middleware language
func Handle(w http.ResponseWriter, r *http.Request) {
	var (
		err              error
		rb               []byte
		iplantGroupsURL  string
		iplantGroupsUser string
		responseBody     []byte
	)

	iplantGroupsURL = os.Getenv("IPLANT_GROUPS_URL")
	iplantGroupsUser = os.Getenv("IPLANT_GROUPS_USER")

	if iplantGroupsURL == "" {
		panic("IPLANT_GROUPS_URL was not set")
	}

	if iplantGroupsUser == "" {
		panic("IPLANT_GROUPS_USER was not set")
	}

	fmt.Printf("iplant-groups URL is %s\n", iplantGroupsURL)

	rb, err = ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, errors.Wrap(err, "error reading request body").Error(), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	userRequest := &UserRequest{}

	if err = json.Unmarshal(rb, userRequest); err != nil {
		http.Error(w, errors.Wrap(err, "error unmarshalling request body").Error(), http.StatusBadRequest)
		return
	}

	if userRequest.Username == "" {
		http.Error(w, "username field was empty", http.StatusBadRequest)
		return
	}

	user := NewUser(ParseID(userRequest.Username), iplantGroupsUser, iplantGroupsURL)
	if err = user.Get(); err != nil {
		http.Error(w, errors.Wrapf(err, "failed to get user info for %s", userRequest.Username).Error(), http.StatusInternalServerError)
		return
	}

	if responseBody, err = json.Marshal(user); err != nil {
		http.Error(w, errors.Wrapf(err, "failed to marshal user info for %s", userRequest.Username).Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, string(responseBody))
}
