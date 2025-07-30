# -*- coding: utf-8 -*-
"""Provides core functionalities for the "rds_custom" MCP toolset.

This module contains the engine-agnostic logic and serves as the **required
base dependency** for all engine-specific tools. It can also be loaded
stand-alone for basic operations.

Toolsets are loaded at runtime via the `--toolsets` command-line argument
or a corresponding environment variable.

Command-Line Usage:
-------------------
1.  **Base Usage Only:**
    To load only the base functionalities, specify `rds_custom` by itself.

2.  **Single-Engine Usage:**
    To use tools for a specific engine (e.g., SQL Server), you MUST include
    **both** the base toolset `rds_custom` AND the engine-specific toolset
    `rds_custom_mssql` in the list, separated by a comma.

Command-Line Examples:
----------------------
# Scenario 1: Basic usage with only the base toolset
# python server.py --toolsets rds_custom

# Scenario 2: Usage for SQL Server
# python server.py --toolsets rds_custom,rds_custom_mssql
"""

import logging
from typing import Dict, Any, Optional, List
import alibabacloud_rds20140815.models as RdsApiModels
from .aliyun_openapi_gateway import AliyunServiceGateway
from . import tool


logger = logging.getLogger(__name__)

RDS_CUSTOM_GROUP_NAME = 'rds_custom'

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instances(region_id: str, instance_id: str|None = None) -> Dict[str, Any]:
    """
    describe rds custom instances.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_id: The ID of a specific instance. If omitted, all instances in the region are returned.

    Returns:
        dict[str, Any]: The response containing instance metadata.
    """
    request = RdsApiModels.DescribeRCInstancesRequest(
        region_id=region_id,
        instance_id=instance_id
    )
    rds_client = AliyunServiceGateway(region_id).rds()
    return rds_client.describe_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_attribute(region_id: str,instance_id: str) -> Dict[str, Any]:
    """
    describe a single rds custom instance's details.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.

    Returns:
        dict[str, Any]: The response containing the instance details.
    """
    request = RdsApiModels.DescribeRCInstanceAttributeRequest(
        region_id=region_id,
        instance_id=instance_id
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_attribute_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def resize_rc_instance_disk(
    region_id: str,
    instance_id: str,
    new_size: int,
    disk_id: str,
    auto_pay: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    resize a specific rds custom instance's disk.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        new_size: The target size of the disk in GiB.
        disk_id: The ID of the cloud disk.
        auto_pay: Specifies whether to enable automatic payment. Default is false.
        dry_run: Specifies whether to perform a dry run. Default is false.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.ResizeRCInstanceDiskRequest(
        region_id=region_id,
        instance_id=instance_id,
        new_size=new_size,
        disk_id=disk_id,
        auto_pay=auto_pay,
        dry_run=dry_run,
        type='online'
    )
    return AliyunServiceGateway(region_id).rds().resize_rcinstance_disk_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_vnc_url(
    region_id: str,
    instance_id: str,
    db_type: str
) -> Dict[str, Any]:
    """
    describe the vnc login url for a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance.
        db_type: The database type, e.g., 'mysql' or 'mssql'.

    Returns:
        dict[str, Any]: The response containing the VNC login URL.
    """
    request = RdsApiModels.DescribeRCInstanceVncUrlRequest(
        region_id=region_id,
        instance_id=instance_id,
        db_type=db_type
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_vnc_url_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def modify_rc_instance_attribute(
    region_id: str,
    instance_id: str,
    password: Optional[str] = None,
    reboot: Optional[bool] = None,
    host_name: Optional[str] = None,
    security_group_id: Optional[str] = None,
    deletion_protection: Optional[bool] = None
) -> Dict[str, Any]:
    """
    modify attributes of a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance to modify.
        password: The new password for the instance.
        reboot: Specifies whether to restart the instance after modification.
        host_name: The new hostname for the instance.
        security_group_id: The ID of the new security group for the instance.
        deletion_protection: Specifies whether to enable the deletion protection feature.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.ModifyRCInstanceAttributeRequest(
        region_id=region_id,
        instance_id=instance_id,
        password=password,
        reboot=reboot,
        host_name=host_name,
        security_group_id=security_group_id,
        deletion_protection=deletion_protection
    )
    return AliyunServiceGateway(region_id).rds().modify_rcinstance_attribute_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def modify_rc_instance_description(
    region_id: str,
    instance_id: str,
    instance_description: str
) -> Dict[str, Any]:
    """
    modify the description of a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to modify.
        instance_description: The new description for the instance.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """

    request = RdsApiModels.ModifyRCInstanceDescriptionRequest(
        region_id=region_id,
        instance_id=instance_id,
        instance_description=instance_description
    )
    return AliyunServiceGateway(region_id).rds().modify_rcinstance_description_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_snapshots(
    region_id: str,
    disk_id: Optional[str] = None,
    snapshot_ids: Optional[List[str]] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Query the list of RDS Custom snapshots information.

    Args:
        region_id: The region ID. You can call DescribeRegions to obtain the latest region list.
        disk_id: The specified cloud disk ID.
        snapshot_ids: The list of snapshot IDs.
        page_number: The page number to return.
        page_size: The number of entries to return on each page. Value range: 30~100. Default value: 30.

    Returns:
        dict[str, Any]: The response containing the list of snapshots and pagination information.
    """

    request = RdsApiModels.DescribeRCSnapshotsRequest(
        region_id=region_id,
        disk_id=disk_id,
        snapshot_ids=snapshot_ids,
        page_number=page_number,
        page_size=page_size
    )

    return AliyunServiceGateway(region_id).rds().describe_rcsnapshots_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def create_rc_snapshot(
    region_id: str,
    disk_id: str,
    description: Optional[str] = None,
    retention_days: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a manual snapshot for a specific cloud disk of an RDS Custom instance.

    Args:
        region_id: The region ID. You can call DescribeRegions to obtain the latest region list.
        disk_id: The ID of the cloud disk for which to create a snapshot.
        description: The description of the snapshot. It must be 2 to 256 characters in length and cannot start with http:// or https://.
        retention_days: The retention period of the snapshot, in days. After the retention period expires, the snapshot is automatically released. Value range: 1 to 65536.

    Returns:
        dict[str, Any]: A dictionary containing the RequestId and the ID of the new snapshot.
    """
    request = RdsApiModels.CreateRCSnapshotRequest(
        region_id=region_id,
        disk_id=disk_id,
        description=description,
        retention_days=retention_days
    )

    return AliyunServiceGateway(region_id).rds().create_rcsnapshot_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_disks(
    region_id: str,
    instance_id: Optional[str] = None,
    disk_ids: Optional[List[str]] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    tag: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Query the list of disks for an RDS Custom instance.

    Args:
        region_id: The region ID. You can call DescribeRegions to obtain the latest region list.
        instance_id: The ID of the instance to which the disks belong.
        disk_ids: The list of disk IDs to query. Supports up to 100 IDs.
        page_number: The page number to return.
        page_size: The number of entries to return on each page. Value range: 30 to 100. Default value: 30.
        tag: A list of tags to filter results. For example: [{"Key": "your_key", "Value": "your_value"}].

    Returns:
        dict[str, Any]: A dictionary containing the list of disks and pagination information.
    """
    request = RdsApiModels.DescribeRCDisksRequest(
        region_id=region_id,
        instance_id=instance_id,
        disk_ids=disk_ids,
        page_number=page_number,
        page_size=page_size,
        tag=tag
    )
    return AliyunServiceGateway(region_id).rds().describe_rcdisks_with_options(request)


@tool(group=RDS_CUSTOM_GROUP_NAME)
async def run_rc_instances(
        region_id: str,
        instance_type: str,
        password: str,
        vswitch_id: str,
        security_group_id: str,
        zone_id: str,
        image_id: str,
        # --- Optional Parameters ---
        instance_charge_type: Optional[str] = None,
        amount: Optional[int] = None,
        period: Optional[int] = None,
        period_unit: Optional[str] = None,
        auto_renew: Optional[bool] = None,
        auto_pay: Optional[bool] = None,
        client_token: Optional[str] = None,
        auto_use_coupon: Optional[bool] = None,
        promotion_code: Optional[str] = None,
        data_disk: Optional[List[Dict[str, Any]]] = None,
        system_disk: Optional[Dict[str, Any]] = None,
        deployment_set_id: Optional[str] = None,
        internet_max_bandwidth_out: Optional[int] = None,
        description: Optional[str] = None,
        key_pair_name: Optional[str] = None,
        dry_run: Optional[bool] = None,
        tag: Optional[List[Dict[str, str]]] = None,
        resource_group_id: Optional[str] = None,
        create_mode: Optional[str] = None,
        host_name: Optional[str] = None,
        spot_strategy: Optional[str] = None,
        support_case: Optional[str] = None,
        create_ack_edge_param: Optional[Dict[str, Any]] = None,
        user_data: Optional[str] = None,
        user_data_in_base_64: Optional[bool] = None,
        deletion_protection: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Creates one or more RDS Custom instances by converting dicts to model objects internally.

    Args:
        region_id: The region ID.
        instance_type: The instance specification. See RDS Custom instance specification list for details.
        password: The password for the instance. It must be 8 to 30 characters long and contain at least three of the following character types: uppercase letters, lowercase letters, digits, and special characters.
        vswitch_id: The vSwitch ID for the target instance.
        security_group_id: The ID of the security group to which the instance belongs.
        zone_id: The zone ID to which the instance belongs.
        image_id: The image ID used by the instance.
        instance_charge_type: The billing method. Valid values: Prepaid (subscription), PostPaid (pay-as-you-go).
        amount: The number of RDS Custom instances to create. Default is 1.
        period: The subscription duration of the resource. Used when instance_charge_type is 'Prepaid'.
        period_unit: The unit of the subscription duration. Valid values: Month, Year.
        auto_renew: Specifies whether to enable auto-renewal for the subscription.
        auto_pay: Specifies whether to enable automatic payment.
        client_token: A client token used to ensure the idempotence of the request.
        auto_use_coupon: Specifies whether to automatically use coupons.
        promotion_code: The coupon code.
        data_disk: The list of data disks. Example: [{"Size": 50, "Category": "cloud_essd"}]
        system_disk: The system disk specification. Example: {"Size": 60, "Category": "cloud_essd"}
        deployment_set_id: The deployment set ID.
        internet_max_bandwidth_out: The maximum public outbound bandwidth in Mbit/s for Custom for SQL Server.
        description: The description of the instance.
        key_pair_name: The name of the key pair.
        dry_run: Specifies whether to perform a dry run to check the request.
        tag: A list of tags to attach to the instance. Example: [{"Key": "your_key", "Value": "your_value"}].
        resource_group_id: The resource group ID.
        create_mode: Whether to allow joining an ACK cluster. '1' means allowed.
        host_name: The hostname of the instance.
        spot_strategy: The bidding strategy for the pay-as-you-go instance.
        support_case: The RDS Custom edition. 'share' or 'exclusive'.
        create_ack_edge_param: Information for the ACK Edge cluster.
        user_data: Custom data for the instance, up to 32 KB in raw format.
        user_data_in_base_64: Whether the custom data is Base64 encoded.
        deletion_protection: Specifies whether to enable release protection.

    Returns:
        dict[str, Any]: A dictionary containing the OrderId, RequestId, and the set of created instance IDs.
    """
    system_disk_obj = None
    if system_disk:
        system_disk_obj = RdsApiModels.RunRCInstancesRequestSystemDisk(**system_disk)
    data_disk_objs = None
    if data_disk:
        data_disk_objs = [RdsApiModels.RunRCInstancesRequestDataDisk(**disk) for disk in data_disk]
    tag_objs = None
    if tag:
        tag_objs = [RdsApiModels.RunRCInstancesRequestTag(**t) for t in tag]
    request = RdsApiModels.RunRCInstancesRequest(
        region_id=region_id,
        instance_type=instance_type,
        password=password,
        v_switch_id=vswitch_id,
        security_group_id=security_group_id,
        zone_id=zone_id,
        image_id=image_id,
        instance_charge_type=instance_charge_type,
        amount=amount,
        period=period,
        period_unit=period_unit,
        auto_renew=auto_renew,
        auto_pay=auto_pay,
        client_token=client_token,
        auto_use_coupon=auto_use_coupon,
        promotion_code=promotion_code,
        deployment_set_id=deployment_set_id,
        internet_max_bandwidth_out=internet_max_bandwidth_out,
        description=description,
        key_pair_name=key_pair_name,
        dry_run=dry_run,
        resource_group_id=resource_group_id,
        create_mode=create_mode,
        host_name=host_name,
        spot_strategy=spot_strategy,
        support_case=support_case,
        create_ack_edge_param=create_ack_edge_param,
        user_data=user_data,
        user_data_in_base_64=user_data_in_base_64,
        deletion_protection=deletion_protection,
        # 传入转换后的模型对象
        system_disk=system_disk_obj,
        data_disk=data_disk_objs,
        tag=tag_objs
    )
    return AliyunServiceGateway(region_id).rds().run_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def get_current_time() -> Dict[str, Any]:
    """Get the current time.

    Returns:
        Dict[str, Any]: The response containing the current time.
    """
    import datetime
    try:
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "current_time": formatted_time
        }
    except Exception as e:
        logger.error(f"Error occurred while getting the current time: {str(e)}")
        raise Exception(f"Failed to get the current time: {str(e)}")
