# 列出节点主要参数是否正常
kubectl get nodes -o go-template='{{range .items}}{{$node := .}}{{range .status.conditions}}{{$node.metadata.name}}{{": "}}{{.type}}{{":"}}{{.status}}{{"\n"}}{{end}}{{end}}'
emeng-h110-4s: MemoryPressure:False
emeng-h110-4s: DiskPressure:False
emeng-h110-4s: PIDPressure:False
emeng-h110-4s: Ready:True

# 查看namespaces信息
kubectl -n public get events

# 集群与server通信是有agent进行的
kubectl -n cattle-system get pods -l app=cattle-agent -o wide
