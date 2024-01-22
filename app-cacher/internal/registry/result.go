package registry

import (
	"github.com/CrusaderX/cacher/internal/fetcher"
)

type Result struct {
	FetcherID string
	Values    []*fetcher.Namespace
}
