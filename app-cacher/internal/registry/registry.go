package registry

import (
	"sync"
	"time"

	"github.com/CrusaderX/cacher/internal/fetcher"
)

type FetcherRegistry struct {
	fetchers map[string]fetcher.Fetcher
	results  chan Result
	period   time.Duration
}

func NewFetcherRegistry(period time.Duration) *FetcherRegistry {
	return &FetcherRegistry{
		fetchers: make(map[string]fetcher.Fetcher),
		results:  make(chan Result),
		period:   period,
	}
}

func (r *FetcherRegistry) Close() {
	close(r.results)
}

func (r *FetcherRegistry) Results() <-chan Result {
	return r.results
}

func (r *FetcherRegistry) Register(fetcher fetcher.Fetcher) {
	r.fetchers[fetcher.Name()] = fetcher
}

func (r *FetcherRegistry) send(wg *sync.WaitGroup, f fetcher.Fetcher) {
	defer wg.Done()

	values := f.Fetch()
	r.results <- Result{
		FetcherID: f.Name(),
		Values:    values,
	}
}

func (r *FetcherRegistry) do() {
	wg := sync.WaitGroup{}

	for _, fth := range r.fetchers {
		wg.Add(1)

		go r.send(&wg, fth)
	}
	wg.Wait()
}

func (r *FetcherRegistry) Fetch() {

	for _ = range time.Tick(r.period) {
		r.do()
	}
}
