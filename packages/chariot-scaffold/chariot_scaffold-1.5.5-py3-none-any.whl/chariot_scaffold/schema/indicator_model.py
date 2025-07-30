from typing import Annotated
from pydantic import BaseModel, field_validator, Field


class IndicatorModel(BaseModel):
    """威胁情报指标模型"""
    
    indicator: Annotated[str, "风险数据值"] = None
    tags: Annotated[list[str], "标签"] = Field(default_factory=list)
    ip: Annotated[str, "源IP"] = None
    hash_: Annotated[str, "哈希"] = None
    domain: Annotated[str, "域名"] = None
    server: Annotated[str, "C&C服务器"] = None
    port: Annotated[str, "端口"] = None
    correlated_ip: Annotated[str, "目的IP"] = None
    type_: Annotated[str, "威胁类型"] = None
    threat_level: Annotated[str, "威胁等级：low(低)/medium(中)/high(高)/urgent(紧急)"] = "low"
    status: Annotated[str, "威胁状态"] = None
    description: Annotated[str, "描述"] = None
    happened_at: Annotated[str, "威胁发生时间"] = None
    software_name: Annotated[str, "恶意软件名称"] = None
    software_type: Annotated[str, "恶意软件类型"] = None
    dispersion_method: Annotated[str, "散布方式"] = None
    sample: Annotated[str, "恶意软件样本"] = None
    target: Annotated[str, "恶意软件目标系统"] = None
    source: Annotated[str, "威胁情报信息来源"] = None
    source_title: Annotated[str, "数据源标题，过滤空值"] = None
    reliability: Annotated[str, "可靠性：low(低)/medium(中)/high(高)"] = "low"
    release_at: Annotated[str, "情报发布时间"] = None
    format_: Annotated[str, "格式"] = None
    alarm_ip: Annotated[str, "告警设备ip"] = None
    raw_id: Annotated[str, "原始情报ID"] = None
    incidents: Annotated[str, "相关事件"] = None
    advises: Annotated[str, "应对建议"] = None

    @field_validator("threat_level")
    @classmethod
    def threat_level_value_check(cls, v):
        """威胁等级字段验证"""
        threat_level_enum = ['low', 'medium', 'high', 'urgent']
        if v and v not in threat_level_enum:
            raise ValueError(f"威胁等级参数非法，必须为以下值之一: {threat_level_enum}")
        return v

    @field_validator("reliability")
    @classmethod
    def reliability_value_check(cls, v):
        """可靠性字段验证"""
        reliability_enum = ['low', 'medium', 'high']
        if v and v not in reliability_enum:
            raise ValueError(f"可靠性参数非法，必须为以下值之一: {reliability_enum}")
        return v
