# K8s config

This uses Kustomize.

When you add something, run `rm kustomization.yaml && kustomize create --autodetect --namespace infinigram-api` in the folder you added something to. Or just add it to the `resources` field of the `kustomization.yaml`.