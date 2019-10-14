package function

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/dghubble/sling"
	"github.com/pkg/errors"
	log "github.com/sirupsen/logrus"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

// Analyses contains the list of analyses running the cluster.
type Analyses struct {
	Analyses []string `json:"analyses"`
}

// IDRequest is the format for requests to the get-analysis-id function
type IDRequest struct {
	ExternalID string `json:"external_id"`
}

// IDResponse is the format for response bodies from the get-analysis-id funciton
type IDResponse struct {
	ID string `json:"id"`
}

// Handle is the entrypoint for OpenFaaS
func Handle(w http.ResponseWriter, r *http.Request) {
	log.SetReportCaller(true)

	viceNamespace := os.Getenv("VICE_NAMESPACE")
	gatewayURL := os.Getenv("GATEWAY")

	if viceNamespace == "" {
		log.Fatal("VICE_NAMESPACE must be set")
	}

	if gatewayURL == "" {
		log.Fatal("GATEWAY must be set")
	}

	gateway := sling.New().Base(gatewayURL)

	config, err := rest.InClusterConfig()
	if err != nil {
		log.Fatal(errors.Wrapf(err, "error loading the config inside the cluster"))
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatal(errors.Wrap(err, "error creating clientset from config"))
	}

	output := &Analyses{
		Analyses: []string{},
	}

	deplist, err := clientset.AppsV1().Deployments(viceNamespace).List(metav1.ListOptions{})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	for _, deployment := range deplist.Items {
		IDReq := &IDRequest{
			ExternalID: deployment.Name,
		}
		IDResp := &IDResponse{}
		resp, err := gateway.Path("/function/get-analysis-id").BodyJSON(IDReq).ReceiveSuccess(IDResp)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		if resp.StatusCode < 200 || resp.StatusCode > 399 {
			http.Error(w, fmt.Errorf("status code from get-analysis-id was %d", resp.StatusCode).Error(), http.StatusInternalServerError)
			return
		}

		output.Analyses = append(output.Analyses, IDResp.ID)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(output)
}
