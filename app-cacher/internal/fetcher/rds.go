package fetcher

import (
	"github.com/CrusaderX/cacher/internal/utils"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/service/rds"
)

type Rds struct {
	name    string
	tag     string
	session *rds.RDS
}

func NewRds(name, tag string, session *rds.RDS) *Rds {
	return &Rds{
		name:    name,
		tag:     tag,
		session: session,
	}
}

func (r *Rds) Name() string {
	return r.name
}

var logger *utils.Logger

func init() {
	logger = utils.NewLogger()
}

func (r *Rds) Fetch() []*Namespace {
	instances, err := r.session.DescribeDBInstances(&rds.DescribeDBInstancesInput{})
	if err != nil {
		if aerr, ok := err.(awserr.Error); ok {
			switch aerr.Code() {
			default:
				logger.Error.Println(aerr.Error())
			}
		} else {
			logger.Error.Println(err.Error())
		}
		return nil
	}

	namespaces := make(map[string]*Namespace)

	for _, i := range instances.DBInstances {
		var namespace *string
		isSchedulerEnabled := false
		for _, t := range i.TagList {
			if *t.Key == "scheduler" && *t.Value == "enabled" {
				isSchedulerEnabled = true
				continue
			}
			if *t.Key == "namespace" {
				namespace = t.Value
			}
		}
		if !isSchedulerEnabled {
			continue
		}
		if namespace == nil {
			logger.Warning.Printf("no namespace for rds %s. skipping.\n", *i.DBInstanceIdentifier)
			continue
		}
		if _, ok := namespaces[*namespace]; !ok {
			namespaces[*namespace] = NewNamespace(*namespace)
		}
		namespaces[*namespace].Add(*i.DBInstanceIdentifier)
	}

	namespacesLst := make([]*Namespace, 0)
	for _, namespace := range namespaces {
		namespacesLst = append(namespacesLst, namespace)
	}

	return namespacesLst
}
