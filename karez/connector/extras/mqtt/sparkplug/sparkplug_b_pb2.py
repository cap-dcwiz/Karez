# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sparkplug_b.proto
"""Generated protocol buffer code."""

from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x11sparkplug_b.proto\x12\x19org.eclipse.tahu.protobuf"\xee\x15\n\x07Payload\x12\x11\n\ttimestamp\x18\x01 \x01(\x04\x12:\n\x07metrics\x18\x02 \x03(\x0b\x32).org.eclipse.tahu.protobuf.Payload.Metric\x12\x0b\n\x03seq\x18\x03 \x01(\x04\x12\x0c\n\x04uuid\x18\x04 \x01(\t\x12\x0c\n\x04\x62ody\x18\x05 \x01(\x0c\x1a\xa6\x04\n\x08Template\x12\x0f\n\x07version\x18\x01 \x01(\t\x12:\n\x07metrics\x18\x02 \x03(\x0b\x32).org.eclipse.tahu.protobuf.Payload.Metric\x12I\n\nparameters\x18\x03 \x03(\x0b\x32\x35.org.eclipse.tahu.protobuf.Payload.Template.Parameter\x12\x14\n\x0ctemplate_ref\x18\x04 \x01(\t\x12\x15\n\ris_definition\x18\x05 \x01(\x08\x1a\xca\x02\n\tParameter\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\r\x12\x13\n\tint_value\x18\x03 \x01(\rH\x00\x12\x14\n\nlong_value\x18\x04 \x01(\x04H\x00\x12\x15\n\x0b\x66loat_value\x18\x05 \x01(\x02H\x00\x12\x16\n\x0c\x64ouble_value\x18\x06 \x01(\x01H\x00\x12\x17\n\rboolean_value\x18\x07 \x01(\x08H\x00\x12\x16\n\x0cstring_value\x18\x08 \x01(\tH\x00\x12h\n\x0f\x65xtension_value\x18\t \x01(\x0b\x32M.org.eclipse.tahu.protobuf.Payload.Template.Parameter.ParameterValueExtensionH\x00\x1a#\n\x17ParameterValueExtension*\x08\x08\x01\x10\x80\x80\x80\x80\x02\x42\x07\n\x05value*\x08\x08\x06\x10\x80\x80\x80\x80\x02\x1a\x97\x04\n\x07\x44\x61taSet\x12\x16\n\x0enum_of_columns\x18\x01 \x01(\x04\x12\x0f\n\x07\x63olumns\x18\x02 \x03(\t\x12\r\n\x05types\x18\x03 \x03(\r\x12<\n\x04rows\x18\x04 \x03(\x0b\x32..org.eclipse.tahu.protobuf.Payload.DataSet.Row\x1a\xaf\x02\n\x0c\x44\x61taSetValue\x12\x13\n\tint_value\x18\x01 \x01(\rH\x00\x12\x14\n\nlong_value\x18\x02 \x01(\x04H\x00\x12\x15\n\x0b\x66loat_value\x18\x03 \x01(\x02H\x00\x12\x16\n\x0c\x64ouble_value\x18\x04 \x01(\x01H\x00\x12\x17\n\rboolean_value\x18\x05 \x01(\x08H\x00\x12\x16\n\x0cstring_value\x18\x06 \x01(\tH\x00\x12h\n\x0f\x65xtension_value\x18\x07 \x01(\x0b\x32M.org.eclipse.tahu.protobuf.Payload.DataSet.DataSetValue.DataSetValueExtensionH\x00\x1a!\n\x15\x44\x61taSetValueExtension*\x08\x08\x01\x10\x80\x80\x80\x80\x02\x42\x07\n\x05value\x1aZ\n\x03Row\x12I\n\x08\x65lements\x18\x01 \x03(\x0b\x32\x37.org.eclipse.tahu.protobuf.Payload.DataSet.DataSetValue*\x08\x08\x02\x10\x80\x80\x80\x80\x02*\x08\x08\x05\x10\x80\x80\x80\x80\x02\x1a\xe9\x03\n\rPropertyValue\x12\x0c\n\x04type\x18\x01 \x01(\r\x12\x0f\n\x07is_null\x18\x02 \x01(\x08\x12\x13\n\tint_value\x18\x03 \x01(\rH\x00\x12\x14\n\nlong_value\x18\x04 \x01(\x04H\x00\x12\x15\n\x0b\x66loat_value\x18\x05 \x01(\x02H\x00\x12\x16\n\x0c\x64ouble_value\x18\x06 \x01(\x01H\x00\x12\x17\n\rboolean_value\x18\x07 \x01(\x08H\x00\x12\x16\n\x0cstring_value\x18\x08 \x01(\tH\x00\x12K\n\x11propertyset_value\x18\t \x01(\x0b\x32..org.eclipse.tahu.protobuf.Payload.PropertySetH\x00\x12P\n\x12propertysets_value\x18\n \x01(\x0b\x32\x32.org.eclipse.tahu.protobuf.Payload.PropertySetListH\x00\x12\x62\n\x0f\x65xtension_value\x18\x0b \x01(\x0b\x32G.org.eclipse.tahu.protobuf.Payload.PropertyValue.PropertyValueExtensionH\x00\x1a"\n\x16PropertyValueExtension*\x08\x08\x01\x10\x80\x80\x80\x80\x02\x42\x07\n\x05value\x1ag\n\x0bPropertySet\x12\x0c\n\x04keys\x18\x01 \x03(\t\x12@\n\x06values\x18\x02 \x03(\x0b\x32\x30.org.eclipse.tahu.protobuf.Payload.PropertyValue*\x08\x08\x03\x10\x80\x80\x80\x80\x02\x1a`\n\x0fPropertySetList\x12\x43\n\x0bpropertyset\x18\x01 \x03(\x0b\x32..org.eclipse.tahu.protobuf.Payload.PropertySet*\x08\x08\x02\x10\x80\x80\x80\x80\x02\x1a\xa4\x01\n\x08MetaData\x12\x15\n\ris_multi_part\x18\x01 \x01(\x08\x12\x14\n\x0c\x63ontent_type\x18\x02 \x01(\t\x12\x0c\n\x04size\x18\x03 \x01(\x04\x12\x0b\n\x03seq\x18\x04 \x01(\x04\x12\x11\n\tfile_name\x18\x05 \x01(\t\x12\x11\n\tfile_type\x18\x06 \x01(\t\x12\x0b\n\x03md5\x18\x07 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x08 \x01(\t*\x08\x08\t\x10\x80\x80\x80\x80\x02\x1a\xbf\x05\n\x06Metric\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05\x61lias\x18\x02 \x01(\x04\x12\x11\n\ttimestamp\x18\x03 \x01(\x04\x12\x10\n\x08\x64\x61tatype\x18\x04 \x01(\r\x12\x15\n\ris_historical\x18\x05 \x01(\x08\x12\x14\n\x0cis_transient\x18\x06 \x01(\x08\x12\x0f\n\x07is_null\x18\x07 \x01(\x08\x12=\n\x08metadata\x18\x08 \x01(\x0b\x32+.org.eclipse.tahu.protobuf.Payload.MetaData\x12\x42\n\nproperties\x18\t \x01(\x0b\x32..org.eclipse.tahu.protobuf.Payload.PropertySet\x12\x13\n\tint_value\x18\n \x01(\rH\x00\x12\x14\n\nlong_value\x18\x0b \x01(\x04H\x00\x12\x15\n\x0b\x66loat_value\x18\x0c \x01(\x02H\x00\x12\x16\n\x0c\x64ouble_value\x18\r \x01(\x01H\x00\x12\x17\n\rboolean_value\x18\x0e \x01(\x08H\x00\x12\x16\n\x0cstring_value\x18\x0f \x01(\tH\x00\x12\x15\n\x0b\x62ytes_value\x18\x10 \x01(\x0cH\x00\x12\x43\n\rdataset_value\x18\x11 \x01(\x0b\x32*.org.eclipse.tahu.protobuf.Payload.DataSetH\x00\x12\x45\n\x0etemplate_value\x18\x12 \x01(\x0b\x32+.org.eclipse.tahu.protobuf.Payload.TemplateH\x00\x12Y\n\x0f\x65xtension_value\x18\x13 \x01(\x0b\x32>.org.eclipse.tahu.protobuf.Payload.Metric.MetricValueExtensionH\x00\x1a \n\x14MetricValueExtension*\x08\x08\x01\x10\x80\x80\x80\x80\x02\x42\x07\n\x05value*\x08\x08\x06\x10\x80\x80\x80\x80\x02*\xf2\x03\n\x08\x44\x61taType\x12\x0b\n\x07Unknown\x10\x00\x12\x08\n\x04Int8\x10\x01\x12\t\n\x05Int16\x10\x02\x12\t\n\x05Int32\x10\x03\x12\t\n\x05Int64\x10\x04\x12\t\n\x05UInt8\x10\x05\x12\n\n\x06UInt16\x10\x06\x12\n\n\x06UInt32\x10\x07\x12\n\n\x06UInt64\x10\x08\x12\t\n\x05\x46loat\x10\t\x12\n\n\x06\x44ouble\x10\n\x12\x0b\n\x07\x42oolean\x10\x0b\x12\n\n\x06String\x10\x0c\x12\x0c\n\x08\x44\x61teTime\x10\r\x12\x08\n\x04Text\x10\x0e\x12\x08\n\x04UUID\x10\x0f\x12\x0b\n\x07\x44\x61taSet\x10\x10\x12\t\n\x05\x42ytes\x10\x11\x12\x08\n\x04\x46ile\x10\x12\x12\x0c\n\x08Template\x10\x13\x12\x0f\n\x0bPropertySet\x10\x14\x12\x13\n\x0fPropertySetList\x10\x15\x12\r\n\tInt8Array\x10\x16\x12\x0e\n\nInt16Array\x10\x17\x12\x0e\n\nInt32Array\x10\x18\x12\x0e\n\nInt64Array\x10\x19\x12\x0e\n\nUInt8Array\x10\x1a\x12\x0f\n\x0bUInt16Array\x10\x1b\x12\x0f\n\x0bUInt32Array\x10\x1c\x12\x0f\n\x0bUInt64Array\x10\x1d\x12\x0e\n\nFloatArray\x10\x1e\x12\x0f\n\x0b\x44oubleArray\x10\x1f\x12\x10\n\x0c\x42ooleanArray\x10 \x12\x0f\n\x0bStringArray\x10!\x12\x11\n\rDateTimeArray\x10"B,\n\x19org.eclipse.tahu.protobufB\x0fSparkplugBProto'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "sparkplug_b_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b"\n\031org.eclipse.tahu.protobufB\017SparkplugBProto"
    )
    _DATATYPE._serialized_start = 2850
    _DATATYPE._serialized_end = 3348
    _PAYLOAD._serialized_start = 49
    _PAYLOAD._serialized_end = 2847
    _PAYLOAD_TEMPLATE._serialized_start = 181
    _PAYLOAD_TEMPLATE._serialized_end = 731
    _PAYLOAD_TEMPLATE_PARAMETER._serialized_start = 391
    _PAYLOAD_TEMPLATE_PARAMETER._serialized_end = 721
    _PAYLOAD_TEMPLATE_PARAMETER_PARAMETERVALUEEXTENSION._serialized_start = 677
    _PAYLOAD_TEMPLATE_PARAMETER_PARAMETERVALUEEXTENSION._serialized_end = 712
    _PAYLOAD_DATASET._serialized_start = 734
    _PAYLOAD_DATASET._serialized_end = 1269
    _PAYLOAD_DATASET_DATASETVALUE._serialized_start = 864
    _PAYLOAD_DATASET_DATASETVALUE._serialized_end = 1167
    _PAYLOAD_DATASET_DATASETVALUE_DATASETVALUEEXTENSION._serialized_start = 1125
    _PAYLOAD_DATASET_DATASETVALUE_DATASETVALUEEXTENSION._serialized_end = 1158
    _PAYLOAD_DATASET_ROW._serialized_start = 1169
    _PAYLOAD_DATASET_ROW._serialized_end = 1259
    _PAYLOAD_PROPERTYVALUE._serialized_start = 1272
    _PAYLOAD_PROPERTYVALUE._serialized_end = 1761
    _PAYLOAD_PROPERTYVALUE_PROPERTYVALUEEXTENSION._serialized_start = 1718
    _PAYLOAD_PROPERTYVALUE_PROPERTYVALUEEXTENSION._serialized_end = 1752
    _PAYLOAD_PROPERTYSET._serialized_start = 1763
    _PAYLOAD_PROPERTYSET._serialized_end = 1866
    _PAYLOAD_PROPERTYSETLIST._serialized_start = 1868
    _PAYLOAD_PROPERTYSETLIST._serialized_end = 1964
    _PAYLOAD_METADATA._serialized_start = 1967
    _PAYLOAD_METADATA._serialized_end = 2131
    _PAYLOAD_METRIC._serialized_start = 2134
    _PAYLOAD_METRIC._serialized_end = 2837
    _PAYLOAD_METRIC_METRICVALUEEXTENSION._serialized_start = 2796
    _PAYLOAD_METRIC_METRICVALUEEXTENSION._serialized_end = 2828
# @@protoc_insertion_point(module_scope)
