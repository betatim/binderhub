import logging
from pprint import pprint

from kubernetes import client, config, watch

config.load_kube_config()
k8s = client.CoreV1Api()

NAME = "build-pod"


def available_nodes():
    ready_nodes = []
    for n in k8s.list_node().items:
        for status in n.status.conditions:
            if status.status == "True" and status.type == "Ready":
                ready_nodes.append(n.metadata.name)
    return ready_nodes


def main():
    logging.info("Starting to watch for pods")
    w = watch.Watch()
    for event in w.stream(k8s.list_namespaced_pod, "default"):
        if (
            event["object"].status.phase == "Pending"
            and event["object"].kind == "Pod"
            and event["object"].spec.scheduler_name == NAME
        ):
            logging.info("A pod we can schedule appeared!")
            print(available_nodes())
            pprint(event)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%X %Z",
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    main()
