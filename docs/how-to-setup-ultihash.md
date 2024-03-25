# HowTo setup UltiHash cluster
<a id="top"></a>
This document describes the installation process of the UltiHash cluster in a Kubernetes environment, both for on-premise or AWS setup.

## Prerequisites
### Data Provided By UltiHash (after the license purchase)
<a id="data_from_uh"></a>
1. Login and password for the UltiHash registry.
   Later in documentation referred as **registry_login** and **registry_password**.
2. License key - referred as **license_key**
3. Monitoring token - referred as **monitoring_token**.
### Remote Environment
1. Dedicated domain name ← to be assigned to your instance of UltiHash cluster.
   (optionally) a valid TLS certificate: for <a href="#inflight_encryption">in-flight encryption</a>.
2. Dedicated Kubernetes cluster. Recommended to use: Kube API version 1.28.
    <div>
    <strong>Info:</strong> You can use any In principle any Kubernetes version starting from 1.20 should be fine - we use vanilla API without any specific extensions.
    </div>

3. Controllers installed:
   - <strong>Ingress controller</strong> - exposes the UltiHash cluster API endpoint outside the Kubernetes cluster for the accessibility. Can be used any, we recommend: the [Nginx Ingress](https://docs.nginx.com/nginx-ingress-controller/). Solution has been tested on Nginx Ingress version 1.9.6.
   - <strong>CSI controller</strong>: manages persistent volumes for the UltiHash cluster components.

       | Provider | Recommended CSI controllers |
       | --- | --- |
       | AWS | https://github.com/kubernetes-sigs/aws-ebs-csi-driver |
       | on-premise | https://github.com/rancher/local-path-provisioner |

      <div>
        <strong>Info:</strong>
           Potentially you can use any CSI controllers, the only requirement is that the controller must be able to dynamically provision and attach persistent volumes.
      </div>

    <div>
        <strong>Warning:</strong>
         ⚠️ To achieve the highest system performance, it is recommended to use the CSI controller that imposes the least disk performance degradation, such as <a href="https://github.com/rancher/local-path-provisioner"> Local Path Provisioner</a>.
    </div>

### Local Environment
- *kubectl* v. 1.28. Make sure it is configured and have access to the Kubernetes cluster.
- *helm* v. 3.*.*

## Installation
The helm chart has to be deployed with dedicated release name and namespace per instance of UltiHash.  The following instructions provide an example of UltiHash setup with:

- release name `<ultihash>`
- namespace `<storage>`

Those names can be changed.

1. Create Kubernetes namespace with the required name
```bash
kubectl create ns <storage>
```
1. Provision there the secret named <**registry-credentials**> -  containing the UltiHash registry credentials (see <a href="data_from_uh"> Data Provided By UltiHash section</a>). Replace <**registry_username**> and <**registry_password**> with the received values.

```bash
kubectl create secret docker-registry <registry-credentials> -n <storage> --docker-server='registry.ultihash.io' --docker-username='<registry_username>' --docker-password='<registry_password>'
```

1. Provision a secret  <**ultihash**> with the license key and monitoring token. Replace <**licence_key**> and <**monitoring_token**> with the actual values received from UH.

```bash
kubectl create secret generic <ultihash> -n <storage> --from-literal=license='<license_key>' --from-literal=token='<monitoring_token>'
```
1. Create cluster configuration setup. See below the example of minimal configuration setup: `values.yaml`. Replace the following placeholders with the actual values:
    - <**storage_class**>- storage class name created by the CSI controller.
    - <**domain_name**> - valid domain name for the UltiHash cluster
    - <**ingress_annotations**> - annotations specific to the Ingress controller running on the Kubernetes cluster. For example, the essential annotations for the Nginx Ingress controller:
        ```bash
              kubernetes.io/ingress.class: nginx
              nginx.ingress.kubernetes.io/proxy-body-size: "0"
        ```
Finally, set the number of replicas and storage size for each service to the desired values.
```yaml
global:                            
  imagePullSecrets:                
    - registry-credentials
  ultihashSecret:          
    name: ultihash
    key: license
  logLevel: INFO                                 
  telemetryExportInterval: 30000

etcd:
  replicaCount: 1
  resources: {}
  affinity: {}
  nodeSelector: {}
  persistence:
    storageClass: <storage_class>
		size**: 8Gi 

entrypoint:
  replicas: 1
  resources: {}
  affinity: {}
  nodeSelector: {}

  service:
    type: ClusterIP                   

  ingress:
    host: <domain_name>             
    annotations:
       <ingress_annotations>                      

storage:
  replicas: 1
  resources: {}
  affinity: {}
  nodeSelector: {}
  storageClass: <storage_class>             
  storageSize: <10Gi>             

deduplicator:
  replicas: 1
  resources: {}
  affinity: {}
  nodeSelector: {}
  storageClass: <storage_class>
  storageSize: <10Gi>

directory:
  replicas: 1
  resources: {}
  affinity: {}
  nodeSelector: {}
  storageClass: <storage_class>
  storageSize: <10Gi>

collector:
  resources: {}
  affinity: {}
  nodeSelector: {}
  extraEnvs:
  - name: UH_POD_IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP
  - name: UH_NODE_IP
    valueFrom:
      fieldRef:
        fieldPath: status.hostIP
  - name: UH_EXPORTER_TOKEN       
    valueFrom:
      secretKeyRef:
        name: ultihash
        key: token
  config:
    receivers:
      kubeletstats: null   # Disable collecting metrics from Kubelet
    service:
      pipelines:
        metrics:
          receivers:
           - otlp
           - prometheus
```
The Helm values shown above will install the following UltiHash cluster components:

- OpenTelemetry collector - collect metrics and logs from application and selected metrics from nodes.
- Prometheus Node Exporter - exposes node metrics to OpenTelemetry Collector (can be switched off, see <a href="adv_config"> Advanced Configuration</a>)
- Etcd and UltiHash Internal Services

   <div>
   <strong>Info:</strong>
   For advanced configuration navigate to the section <a href="adv_config">Advanced Configuration</a>.
   </div>

1. Login into the UltiHash registry via Helm (**registry_username** to be replaced with the actual user name). Input **registry_password** once helm requests it.

   ```bash
   helm registry login -u **registry_username** registry.ultihash.io
   ```

1. Install the Helm chart with the customized values. The release name in the example is set to <**ultihash**>.

   ```bash
   helm install <ultihash> oci://[registry.ultihash.io/stable/ultihash-cluster](http://registry.ultihash.io/stable/ultihash-cluster) -n <storage> --values values.yaml --wait
   ```

Helm will wait until all services of the UltiHash cluster become ready. Once it exits without errors, the UltiHash cluster has been successfully deployed. Use the <**domain_name**> to interact with the UltiHash cluster.



## Advanced Configuration
<a id="adv_config"></a>
### Export telemetry to a custom backend
In order to enable export of telemetry into company monitoring backends, you can add the next changes. See below example, where Prometheus is used for metrics and Loki for logs. Make sure you define unique names for your exporters.

   <div>
   <strong>Info:</strong>
   Name `otlphttp/uptrace` is reserved for the system use.
   </div>

```yaml
collector:
  extraEnvs:
  - name: UH_POD_IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP
  - name: UH_NODE_IP
    valueFrom:
      fieldRef:
        fieldPath: status.hostIP
  - name: UH_EXPORTER_TOKEN      
    valueFrom:
      secretKeyRef:
        name: ultihash
        key: token
  config:                         
    exporters:
      # 1. Define the required exporters e.g. for metrics prometheus, mind unique name
			prometheus/mycompany:
        endpoint: "1.2.3.4:1234"
      # 2. Define the required exporters e.g. for logs loki, mind unique name
      loki/mycompany:
        endpoint: "http://1.2.3.4:3100/loki/api/v1/push"		
    service:
      pipelines:
        logs:
          exporters:
            - debug # please don't change this
            - otlphttp/uptrace # please don't update this
            - loki/mycompany # 3. Assign company exporter for logs
        metrics:
          exporters:
            - debug # please don't update this
            - otlphttp/uptrace # please don't update this
            - prometheus/mycompany # 4. Assign exporter for metrics
```
### Customize Prometheus Node Exporter
To define the custom list of enabled metric collectors, use the configuration block below. In this example Prometheus Node Exporter has only 2 collectors enabled: `cpu` and `diskstats`:

```yaml
exporter:
  enabled: true
  extraArgs:
    - "--collector.disable-defaults"   # please don't change this
    - "--web.disable-exporter-metrics" # please don't change this
    - "--collector.cpu"
    - "--collector.diskstats"
```
By default, the following metric collectors are enabled: `cpu`, `collectorcpufreq`, `diskstats`, `filesystem`, `hwmon`, `loadavg`, `mdadm`, `meminfo`, `netclass`, `netdev`, `netstat`, `nvme`, `powersupplyclass`, `pressure`, `rapl`, `schedstat`, `sockstat`, `thermal_zone`, `meminfo_numa`, `zoneinfo`. For the full list of available collectors refer to [this documentation](https://github.com/prometheus/node_exporter?tab=readme-ov-file#collectors).

### Disable Prometheus Node Exporter
The Helm chart installs [Prometheus Node Exporter](https://github.com/prometheus/node_exporter) by default to collect node metrics. In case it is not required, it could be disabled:

```yaml
collector:
  extraEnvs:
  - name: UH_POD_IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP
  - name: UH_NODE_IP
    valueFrom:
      fieldRef:
        fieldPath: status.hostIP
  - name: UH_EXPORTER_TOKEN     
    valueFrom:
      secretKeyRef:
        name: ultihash
        key: token
  config:                      
    receivers:
      prometheus: null  # Disable node metrics collection
    service:
      pipelines:
        metrics:
          receivers:
            - otlp

exporter:
  enabled: false  # Disable Prometheus Node Exporter
```

### In-Flight Encryption
<a id="inflight_encryption"></a>
It is recommended to configure TLS encryption on the load balancer level rather than on the Ingress level. However, in case Ingress level TLS encryption is required, it could be configured in the way shown below. Replace the <**domain_name**>, and <**ingress_annotations**> with the actual values. Follow [this instruction](https://kubernetes.io/docs/concepts/services-networking/ingress/#tls) to provision the <**tls_secret**>.

```yaml
entrypoint:
  ingress:
    host: <domain_name>            
    annotations:
      <ingress_annotations>
    tls:
     - hosts:
        - <domain_name> 
       secretName: <tls_secret>
```