# helm-charts

## hello-chart

1. 创建hello-chart
```bash
$ helm create hello-chart
```

2. 修改hello-chart/Chart.yaml
3. 修改hello-chart/values.yaml

4. 校验Chart.yaml
```bash
$ helm lint
```

5. 打包
```bash
$ helm package hello-chart --debug
```

6. 更新index.yaml
```bash
$ helm repo index --url https://piaohua.github.io/helm-charts/ --merge index.yaml .
```

7. 提交*.tgz & index.yaml
8. 更新repo
```bash
$ helm repo update
$ helm search list
```

9. 部署hello-chart
```bash
$ helm install piaohua/hello-chart --generate-name --namespace hello

$ export POD_NAME=$(kubectl get pods --namespace hello -l "app.kubernetes.io/name=hello-chart,app.kubernetes.io/instance=hello-chart-1595757801" -o jsonpath="{.items[0].metadata.name}")

$ kubectl --namespace hello port-forward $POD_NAME 8080:80

$ kubectl get deployment,rs,rc,pod -n hello

$ curl -X GET http://127.0.0.1:8080
```

