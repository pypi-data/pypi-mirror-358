class PartitionInfoAws():

    def __init__(self, dataPartitionId: str, tenant_id: str, tenant_ssm_prefix: str):
        self.dataPartitionId = dataPartitionId
        self.tenant_id = tenant_id
        self.tenant_ssm_prefix = tenant_ssm_prefix
