# -*- coding: utf-8 -*-
"""
Provides SQL Server-specific MCP tools for the "rds_custom" product.

This toolset requires the base `rds_custom` toolset to be loaded
simultaneously. See the base module's docstring for detailed usage.
"""
import logging
from typing import Dict, Any, Optional, List
import alibabacloud_rds20140815.models as RdsApiModels

from .aliyun_openapi_gateway import AliyunServiceGateway
from . import tool

logger = logging.getLogger(__name__)

RDS_CUSTOM_GROUP_NAME = 'rds_custom_mssql'

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_ip_address(
    region_id: str,
    instance_id: str,
    ddos_region_id: str,
    instance_type: str = 'ecs',
    resource_type: str = 'ecs',
    ddos_status: Optional[str] = None,
    instance_ip: Optional[str] = None,
    current_page: Optional[int] = None,
    page_size: Optional[int] = None,
    instance_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe the ddos protection details for an rds custom instance.
    Args:
        region_id: The region ID where the Custom instance is located.
        instance_id: The ID of the Custom instance.
        ddos_region_id: The region ID of the public IP asset.
        instance_type: The instance type of the public IP asset, fixed value 'ecs'.
        resource_type: The resource type, fixed value 'ecs'.
        ddos_status: The DDoS protection status of the public IP asset.
        instance_ip: The IP address of the public IP asset to query.
        current_page: The page number of the results to display.
        page_size: The number of instances per page.
        instance_name: The name of the Custom instance.

    Returns:
        dict[str, Any]: The response containing the DDoS protection details.
    """
    request = RdsApiModels.DescribeRCInstanceIpAddressRequest(
        region_id=region_id,
        instance_id=instance_id,
        ddos_region_id=ddos_region_id,
        instance_type=instance_type,
        resource_type=resource_type,
        ddos_status=ddos_status,
        instance_ip=instance_ip,
        current_page=current_page,
        page_size=page_size,
        instance_name=instance_name
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_ip_address_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def stop_rc_instances(
    region_id: str,
    instance_ids: List[str],
    force_stop: bool = False,
    batch_optimization: Optional[str] = None
) -> Dict[str, Any]:
    """
    stop one or more rds custom instances in batch.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_ids: A list of instance IDs to be stopped.
        force_stop: Specifies whether to force stop the instances. Default is false.
        batch_optimization: The batch operation mode.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.StopRCInstancesRequest(
        region_id=region_id,
        instance_ids=instance_ids,
        force_stop=force_stop,
        batch_optimization=batch_optimization
    )
    return AliyunServiceGateway(region_id).rds().stop_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def start_rc_instances(
    region_id: str,
    instance_ids: List[str],
    batch_optimization: Optional[str] = None
) -> Dict[str, Any]:
    """
    start one or more rds custom instances in batch.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_ids: A list of instance IDs to be started.
        batch_optimization: The batch operation mode.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.StartRCInstancesRequest(
        region_id=region_id,
        instance_ids=instance_ids,
        batch_optimization=batch_optimization
    )
    return AliyunServiceGateway(region_id).rds().start_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def reboot_rc_instance(
    region_id: str,
    instance_id: str,
    force_stop: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    reboot a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to reboot.
        force_stop: Specifies whether to force shutdown before rebooting. Default is false.
        dry_run: Specifies whether to perform a dry run only. Default is false.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.RebootRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        force_stop=force_stop,
        dry_run=dry_run
    )
    return AliyunServiceGateway(region_id).rds().reboot_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_image_list(
    region_id: str,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    type: Optional[str] = None,
    architecture: Optional[str] = None,
    image_id: Optional[str] = None,
    image_name: Optional[str] = None,
    instance_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe the list of custom images for creating rds custom instances.

    Args:
        region_id: The region ID to query for images.
        page_number: The page number of the results.
        page_size: The number of records per page.
        type: The image type, currently only 'self' is supported.
        architecture: The system architecture of the image, e.g., 'x86_64'.
        image_id: The ID of a specific image to query.
        image_name: The name of a specific image to query.
        instance_type: The instance type to query usable images for.

    Returns:
        dict[str, Any]: The response containing the list of custom images.
    """
    request = RdsApiModels.DescribeRCImageListRequest(
        region_id=region_id,
        page_number=page_number,
        page_size=page_size,
        type=type,
        architecture=architecture,
        image_id=image_id,
        image_name=image_name,
        instance_type=instance_type
    )

    return AliyunServiceGateway(region_id).rds().describe_rcimage_list_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_metric_list(
    region_id: str,
    instance_id: str,
    metric_name: str,
    start_time: str,
    end_time: str,
    period: Optional[str] = None,
    length: Optional[str] = None,
    next_token: Optional[str] = None,
    dimensions: Optional[str] = None,
    express: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe monitoring data for a specific metric of an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to query.
        metric_name: The metric to be monitored, e.g., 'CPUUtilization'.
        start_time: The start time of the query, format 'YYYY-MM-DD HH:MM:SS'.
        end_time: The end time of the query, format 'YYYY-MM-DD HH:MM:SS'.
        period: The statistical period of the monitoring data in seconds.
        length: The number of entries to return on each page.
        next_token: The pagination token.
        dimensions: The dimensions to query data for multiple resources in batch.
        express: A reserved parameter.

    Returns:
        dict[str, Any]: The response containing the list of monitoring data.
    """
    request = RdsApiModels.DescribeRCMetricListRequest(
        region_id=region_id,
        instance_id=instance_id,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time,
        period=period,
        length=length,
        next_token=next_token,
        dimensions=dimensions,
        express=express
    )

    return AliyunServiceGateway(region_id).rds().describe_rcmetric_list_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def sync_rc_security_group(
    region_id: str,
    instance_id: str,
    security_group_id: str
) -> Dict[str, Any]:
    """
    synchronize the security group rules for an rds sql server custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        security_group_id: The ID of the security group.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.SyncRCSecurityGroupRequest(
        region_id=region_id,
        instance_id=instance_id,
        security_group_id=security_group_id
    )

    return AliyunServiceGateway(region_id).rds().sync_rcsecurity_group_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def associate_eip_address_with_rc_instance(
    region_id: str,
    instance_id: str,
    allocation_id: str
) -> Dict[str, Any]:
    """
    associate an elastic ip address (eip) with an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        allocation_id: The ID of the Elastic IP Address.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.AssociateEipAddressWithRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        allocation_id=allocation_id
    )

    return AliyunServiceGateway(region_id).rds().associate_eip_address_with_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def unassociate_eip_address_with_rc_instance(
    region_id: str,
    instance_id: str,
    allocation_id: str
) -> Dict[str, Any]:
    """
    unassociate an elastic ip address (eip) from an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        allocation_id: The ID of the Elastic IP Address to unassociate.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.UnassociateEipAddressWithRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        allocation_id=allocation_id
    )

    return AliyunServiceGateway(region_id).rds().unassociate_eip_address_with_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_ddos_count(
    region_id: str,
    ddos_region_id: str,
    instance_type: str = 'ecs'
) -> Dict[str, Any]:
    """
    describe the count of ddos attacks on rds custom instances.

    Args:
        region_id: The region ID where the Custom instance is located.
        ddos_region_id: The region ID of the public IP asset to query.
        instance_type: The instance type of the public IP asset, fixed value 'ecs'.

    Returns:
        dict[str, Any]: The response containing the count of ddos attacks.
    """
    request = RdsApiModels.DescribeRCInstanceDdosCountRequest(
        region_id=region_id,
        ddos_region_id=ddos_region_id,
        instance_type=instance_type
    )

    return AliyunServiceGateway(region_id).rds().describe_rcinstance_ddos_count_with_options(request)