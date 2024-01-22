package fetcher

import (
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/ec2"
)

type Ec2 struct {
	name    string
	tag     string
	session *ec2.EC2
}

func NewEc2(name, tag string, session *ec2.EC2) *Ec2 {
	return &Ec2{
		name:    name,
		tag:     tag,
		session: session,
	}
}

func (e *Ec2) Name() string {
	return e.name
}

func (e *Ec2) Fetch() []*Namespace {
	input := &ec2.DescribeInstancesInput{
		Filters: []*ec2.Filter{
			{
				Name: aws.String("tag:scheduler"),
				Values: []*string{
					aws.String(e.tag),
				},
			},
		},
	}
	response, _ := e.session.DescribeInstances(input)
	namespaces := make(map[string]*Namespace)

	for _, res := range response.Reservations {
		for _, instance := range res.Instances {
			var namespace *string
			for _, t := range instance.Tags {
				if *t.Key == "namespace" {
					namespace = t.Value
				}
			}
			if namespace == nil {
				continue
			}

			if _, ok := namespaces[*namespace]; !ok {
				namespaces[*namespace] = NewNamespace(*namespace)
			}
			namespaces[*namespace].Add(*instance.InstanceId)
		}
	}

	namespacesLst := make([]*Namespace, 0)
	for _, namespace := range namespaces {
		namespacesLst = append(namespacesLst, namespace)
	}

	return namespacesLst
}
