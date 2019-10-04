package function

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
)

// Analysis contains the ID for the Analysis, which gets used as the resource
// name when checking permissions.
type Analysis struct {
	ID string `json:"id"` // Literally all we care about here.
}

// Analyses is a list of analyses returned by the apps service.
type Analyses struct {
	Analyses []Analysis `json:"analyses"`
}

// GetAnalysisID returns the Analysis ID returned for the given external ID.
func GetAnalysisID(appsURL, appsUser, externalID string) (*Analysis, error) {
	reqURL, err := url.Parse(appsURL)
	if err != nil {
		return nil, err
	}
	reqURL.Path = filepath.Join(reqURL.Path, "admin/analyses/by-external-id", externalID)

	v := url.Values{}
	v.Set("user", appsUser)
	reqURL.RawQuery = v.Encode()

	resp, err := http.Get(reqURL.String())
	defer func() {
		if resp != nil {
			if resp.Body != nil {
				resp.Body.Close()
			}
		}
	}()
	if err != nil {
		return nil, err
	}

	analyses := &Analyses{}
	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if err = json.Unmarshal(b, analyses); err != nil {
		return nil, err
	}
	if len(analyses.Analyses) < 1 {
		return nil, errors.New("no analyses found")
	}
	return &analyses.Analyses[0], nil
}

// IDRequest is the format that incoming requests should be in.
type IDRequest struct {
	ExternalID string `json:"external_id"`
}

// Handle is the handler for the OpenFaaS golang-middleware language
func Handle(w http.ResponseWriter, r *http.Request) {
	var (
		rb       []byte
		err      error
		appsUser string
		appsURL  string
	)

	appsUser = os.Getenv("APPS_USER")
	appsURL = os.Getenv("APPS_URL")

	rb, err = ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	idReq := &IDRequest{}

	if err = json.Unmarshal(rb, idReq); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if idReq.ExternalID == "" {
		http.Error(w, "external ID must be set", http.StatusBadRequest)
		return
	}

	var analysis *Analysis
	analysis, err = GetAnalysisID(appsURL, appsUser, idReq.ExternalID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(analysis)
}
