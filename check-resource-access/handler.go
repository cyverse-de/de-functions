// check-resource-access
// =====================

// Looks up the permissions that a subject has for a resource. By default, the
// subject type is 'user' and the resource type is 'analysis'. Only performs
// look ups against the permissions service.

package function

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
)

// LookupPair contains the subject and resource for the permissions check.
type LookupPair struct {
	Subject  string `json:"subject"`
	Resource string `json:"resource"`
}

// Handle is the handler for the OpenFaaS golang-middleware language
func Handle(w http.ResponseWriter, r *http.Request) {
	var (
		err          error
		rb           []byte
		permsURL     string
		subjectType  string
		resourceType string
	)

	permsURL = os.Getenv("PERMISSIONS_URL")
	subjectType = os.Getenv("SUBJECT_TYPE")
	resourceType = os.Getenv("RESOURCE_TYPE")

	rb, err = ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	lookup := &LookupPair{}

	if err = json.Unmarshal(rb, lookup); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if lookup.Subject == "" {
		http.Error(w, "subject name was empty", http.StatusBadRequest)
		return
	}

	if lookup.Resource == "" {
		http.Error(w, "resource was empty", http.StatusBadRequest)
		return
	}

	requrl, err := url.Parse(permsURL)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	requrl.Path = filepath.Join(requrl.Path, "permissions/subjects", subjectType, lookup.Subject, resourceType, lookup.Resource)
	resp, err := http.Get(requrl.String())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	fmt.Fprintf(w, string(b))
}
