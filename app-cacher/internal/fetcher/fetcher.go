package fetcher

type Fetcher interface {
	Name() string
	Fetch() []*Namespace
}

type Namespace struct {
	Name string   `json:"name"`
	Ids  []string `json:"ids"`
}

func NewNamespace(name string) *Namespace {
	return &Namespace{
		Name: name,
		Ids:  make([]string, 0),
	}
}

func (n *Namespace) Add(id string) {
	n.Ids = append(n.Ids, id)
}
