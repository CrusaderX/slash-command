package utils

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

const (
	DEFAULT_FETCH_PERIOD = 10
)

type Options struct {
	FetchPeriod       time.Duration
	DynamoDBTableName string
}

func ParseOptionsFromEnv() (*Options, error) {
	fetchPeriod := time.Second * DEFAULT_FETCH_PERIOD
	fetchPeriodEnv := os.Getenv("CACHER_FETCH_PERIOD")
	if fetchPeriodEnv != "" {
		if fetchPeriodFromEnv, err := strconv.Atoi(fetchPeriodEnv); err == nil {
			fetchPeriod = time.Second * time.Duration(fetchPeriodFromEnv)
		}
	}

	dynamodbTable := os.Getenv("CACHER_DYNAMODB_TABLE")
	if dynamodbTable == "" {
		return nil, fmt.Errorf("no env var CACHER_DYNAMODB_TABLE")
	}

	return &Options{
		FetchPeriod:       fetchPeriod,
		DynamoDBTableName: dynamodbTable,
	}, nil
}
