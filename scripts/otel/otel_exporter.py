#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:32:56 2024

@author: massi
"""

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

class otel_exporter:
    metrics = {}
    
    def __init__(self, endpoint, test_name):
        resource = Resource(attributes={
            SERVICE_NAME: "performance-test"
        })
        
        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint, insecure=True, timeout=20))
        meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(meterProvider)
        self.meter = metrics.get_meter(test_name)

    def create_metric (self, metric_name):
        self.metrics[metric_name] = self.meter.create_gauge(metric_name)
        
    def push_value(self, metric_name, val):        
        self.metrics[metric_name].set(val)

