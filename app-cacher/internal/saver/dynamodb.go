package saver

import (
	"encoding/json"
	"fmt"

	"github.com/CrusaderX/cacher/internal/registry"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
)

type DynamoDBSaver struct {
	tableName string
	session   *dynamodb.DynamoDB
}

func NewDynamoDBSaver(tableName string, session *dynamodb.DynamoDB) *DynamoDBSaver {
	return &DynamoDBSaver{
		tableName: tableName,
		session:   session,
	}
}

func (d *DynamoDBSaver) SaveFetcherResult(r *registry.Result) error {
	data, err := json.Marshal(r.Values)
	if err != nil {
		return fmt.Errorf("cannot encode data from %s fetcher", r.FetcherID)
	}

	item := map[string]*dynamodb.AttributeValue{
		"fetcherid": {
			S: aws.String(r.FetcherID),
		},
		"data": {
			S: aws.String(string(data)),
		},
	}

	input := &dynamodb.PutItemInput{
		Item:      item,
		TableName: aws.String(d.tableName),
	}

	_, err = d.session.PutItem(input)
	return err
}
