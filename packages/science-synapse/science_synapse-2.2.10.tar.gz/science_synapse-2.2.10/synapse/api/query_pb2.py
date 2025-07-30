"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/query.proto')
_sym_db = _symbol_database.Default()
from ..api import channel_pb2 as api_dot_channel__pb2
from ..api import status_pb2 as api_dot_status__pb2
from ..api import tap_pb2 as api_dot_tap__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fapi/query.proto\x12\x07synapse\x1a\x11api/channel.proto\x1a\x10api/status.proto\x1a\rapi/tap.proto"G\n\x0bSampleQuery\x12"\n\x08channels\x18\x01 \x03(\x0b2\x10.synapse.Channel\x12\x14\n\x0csample_count\x18\x02 \x01(\r"\'\n\x0eImpedanceQuery\x12\x15\n\relectrode_ids\x18\x01 \x03(\r"&\n\rSelfTestQuery\x12\x15\n\rperipheral_id\x18\x01 \x01(\r"N\n\x14ImpedanceMeasurement\x12\x14\n\x0celectrode_id\x18\x01 \x01(\r\x12\x11\n\tmagnitude\x18\x02 \x01(\x02\x12\r\n\x05phase\x18\x03 \x01(\x02"H\n\x11ImpedanceResponse\x123\n\x0cmeasurements\x18\x01 \x03(\x0b2\x1d.synapse.ImpedanceMeasurement"Y\n\x0cSelfTestItem\x12\x11\n\ttest_name\x18\x01 \x01(\t\x12\x0e\n\x06passed\x18\x02 \x01(\x08\x12\x11\n\ttest_data\x18\x03 \x03(\r\x12\x13\n\x0btest_report\x18\x04 \x01(\t"L\n\x10SelfTestResponse\x12\x12\n\nall_passed\x18\x01 \x01(\x08\x12$\n\x05tests\x18\x02 \x03(\x0b2\x15.synapse.SelfTestItem"\xe7\x02\n\x0cQueryRequest\x123\n\nquery_type\x18\x01 \x01(\x0e2\x1f.synapse.QueryRequest.QueryType\x122\n\x0fimpedance_query\x18\x02 \x01(\x0b2\x17.synapse.ImpedanceQueryH\x00\x12,\n\x0csample_query\x18\x03 \x01(\x0b2\x14.synapse.SampleQueryH\x00\x121\n\x0fself_test_query\x18\x04 \x01(\x0b2\x16.synapse.SelfTestQueryH\x00\x121\n\x0flist_taps_query\x18\x05 \x01(\x0b2\x16.synapse.ListTapsQueryH\x00"Q\n\tQueryType\x12\t\n\x05kNone\x10\x00\x12\x0e\n\nkImpedance\x10\x01\x12\x0b\n\x07kSample\x10\x02\x12\r\n\tkSelfTest\x10\x03\x12\r\n\tkListTaps\x10\x04B\x07\n\x05query"<\n\x12StreamQueryRequest\x12&\n\x07request\x18\x01 \x01(\x0b2\x15.synapse.QueryRequest"\xf6\x01\n\rQueryResponse\x12\x1f\n\x06status\x18\x01 \x01(\x0b2\x0f.synapse.Status\x12\x0c\n\x04data\x18\x02 \x03(\r\x128\n\x12impedance_response\x18\x03 \x01(\x0b2\x1a.synapse.ImpedanceResponseH\x00\x127\n\x12self_test_response\x18\x04 \x01(\x0b2\x19.synapse.SelfTestResponseH\x00\x127\n\x12list_taps_response\x18\x05 \x01(\x0b2\x19.synapse.ListTapsResponseH\x00B\n\n\x08response"\xcc\x01\n\x13StreamQueryResponse\x12!\n\x04code\x18\x01 \x01(\x0e2\x13.synapse.StatusCode\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x14\n\x0ctimestamp_ns\x18\x03 \x01(\x04\x12/\n\timpedance\x18\x04 \x01(\x0b2\x1a.synapse.ImpedanceResponseH\x00\x12.\n\tself_test\x18\x05 \x01(\x0b2\x19.synapse.SelfTestResponseH\x00B\n\n\x08responseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.query_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SAMPLEQUERY']._serialized_start = 80
    _globals['_SAMPLEQUERY']._serialized_end = 151
    _globals['_IMPEDANCEQUERY']._serialized_start = 153
    _globals['_IMPEDANCEQUERY']._serialized_end = 192
    _globals['_SELFTESTQUERY']._serialized_start = 194
    _globals['_SELFTESTQUERY']._serialized_end = 232
    _globals['_IMPEDANCEMEASUREMENT']._serialized_start = 234
    _globals['_IMPEDANCEMEASUREMENT']._serialized_end = 312
    _globals['_IMPEDANCERESPONSE']._serialized_start = 314
    _globals['_IMPEDANCERESPONSE']._serialized_end = 386
    _globals['_SELFTESTITEM']._serialized_start = 388
    _globals['_SELFTESTITEM']._serialized_end = 477
    _globals['_SELFTESTRESPONSE']._serialized_start = 479
    _globals['_SELFTESTRESPONSE']._serialized_end = 555
    _globals['_QUERYREQUEST']._serialized_start = 558
    _globals['_QUERYREQUEST']._serialized_end = 917
    _globals['_QUERYREQUEST_QUERYTYPE']._serialized_start = 827
    _globals['_QUERYREQUEST_QUERYTYPE']._serialized_end = 908
    _globals['_STREAMQUERYREQUEST']._serialized_start = 919
    _globals['_STREAMQUERYREQUEST']._serialized_end = 979
    _globals['_QUERYRESPONSE']._serialized_start = 982
    _globals['_QUERYRESPONSE']._serialized_end = 1228
    _globals['_STREAMQUERYRESPONSE']._serialized_start = 1231
    _globals['_STREAMQUERYRESPONSE']._serialized_end = 1435