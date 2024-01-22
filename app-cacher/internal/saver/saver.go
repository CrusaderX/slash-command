package saver

import (
	"github.com/CrusaderX/cacher/internal/registry"
)

type Saver interface {
	SaveFetcherResult(result *registry.Result) error
}
