package main

import (
	"github.com/CrusaderX/cacher/internal/fetcher"
	"github.com/CrusaderX/cacher/internal/registry"
	"github.com/CrusaderX/cacher/internal/saver"
	"github.com/CrusaderX/cacher/internal/utils"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/ec2"
	"github.com/aws/aws-sdk-go/service/rds"
)

var logger *utils.Logger

func main() {
	logger = utils.NewLogger()
	options, err := utils.ParseOptionsFromEnv()
	if err != nil {
		logger.Error.Fatalln(err.Error())
	}

	reg := registry.NewFetcherRegistry(options.FetchPeriod)
	defer reg.Close()

	awssession, _ := session.NewSession()

	ec2session := ec2.New(awssession)
	rdssession := rds.New(awssession)
	dynamodbsession := dynamodb.New(awssession)

	saver := saver.NewDynamoDBSaver(options.DynamoDBTableName, dynamodbsession)

	reg.Register(fetcher.NewEc2("EC2", "enabled", ec2session))
	reg.Register(fetcher.NewRds("RDS", "enabled", rdssession))

	go reg.Fetch()

	for r := range reg.Results() {
		err := saver.SaveFetcherResult(&r)
		if err != nil {
			logger.Error.Fatalln(err.Error())
		}
		logger.Info.Printf("saved %s fetcher data to dynamodb\n", r.FetcherID)
	}
}
