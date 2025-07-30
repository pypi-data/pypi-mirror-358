from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import os

class MultiCloudTemplateLoader:
    """Enhanced template loader supporting organized multi-cloud structure"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
        
        # Template mapping for backward compatibility
        self.template_mapping = {
            # AWS Compute
            'ec2': 'aws/compute/ec2.tf.j2',
            'lambda_function': 'aws/compute/lambda_function.tf.j2',
            'launch_template': 'aws/compute/launch_template.tf.j2',
            'amis': 'aws/compute/amis.tf.j2',
            
            # AWS Storage  
            's3_bucket': 'aws/storage/s3_bucket.tf.j2',
            'volumes': 'aws/storage/volumes.tf.j2',
            'ebs_snapshot': 'aws/storage/ebs_snapshot.tf.j2',
            
            # AWS Database
            'rds_instance': 'aws/database/rds_instance.tf.j2',
            'rds_subnet_group': 'aws/database/rds_subnet_group.tf.j2',
            'rds_parameter_group': 'aws/database/rds_parameter_group.tf.j2',
            
            # AWS Networking
            'vpc': 'aws/networking/vpc.tf.j2',
            'subnets': 'aws/networking/subnets.tf.j2',
            'security_groups': 'aws/networking/security_groups.tf.j2',
            'elbv2_load_balancer': 'aws/networking/elbv2_load_balancer.tf.j2',
            'elbv2_target_group': 'aws/networking/elbv2_target_group.tf.j2',
            'elbv2_listener': 'aws/networking/elbv2_listener.tf.j2',
            'classic_load_balancer': 'aws/networking/classic_load_balancer.tf.j2',
            'eips': 'aws/networking/eips.tf.j2',
            'network_interfaces': 'aws/networking/network_interfaces.tf.j2',

            # VPC Advanced Features
            'internet_gateway': 'aws/networking/internet_gateway.tf.j2',
            'nat_gateway': 'aws/networking/nat_gateway.tf.j2',
            'route_table': 'aws/networking/route_table.tf.j2',
            'vpc_endpoint': 'aws/networking/vpc_endpoint.tf.j2',
            # AWS DNS
            'route53_zone': 'aws/dns/route53_zone.tf.j2',
            'route53_record': 'aws/dns/route53_record.tf.j2',
            
            # AWS Security
            'iam_roles': 'aws/security/iam_roles.tf.j2',
            'iam_policies': 'aws/security/iam_policies.tf.j2',
            'key_pairs': 'aws/security/key_pairs.tf.j2',
            
            # AWS Integration
            'api_gateway_rest_api': 'aws/integration/api_gateway_rest_api.tf.j2',
            'api_gateway_resource': 'aws/integration/api_gateway_resource.tf.j2',
            'api_gateway_method': 'aws/integration/api_gateway_method.tf.j2',
            'api_gateway_integration': 'aws/integration/api_gateway_integration.tf.j2',
            'api_gateway_deployment': 'aws/integration/api_gateway_deployment.tf.j2',
            'api_gateway_stage': 'aws/integration/api_gateway_stage.tf.j2',
            'lambda_permission': 'aws/integration/lambda_permission.tf.j2',
            
            # AWS Serverless
            'lambda_layer_version': 'aws/serverless/lambda_layer_version.tf.j2',
            
            # AWS Monitoring (CloudWatch)
            'cloudwatch_log_group': 'aws/monitoring/cloudwatch_log_group.tf.j2',
            'cloudwatch_alarm': 'aws/monitoring/cloudwatch_alarm.tf.j2',
            'cloudwatch_dashboard': 'aws/monitoring/cloudwatch_dashboard.tf.j2',

            # Add template mappings
            'ecs_cluster': 'aws/container/ecs_cluster.tf.j2',
            'ecs_service': 'aws/container/ecs_service.tf.j2',
            'ecs_task_definition': 'aws/container/ecs_task_definition.tf.j2',
            'ecr_repository': 'aws/container/ecr_repository.tf.j2',
            'efs_file_system': 'aws/storage/efs_file_system.tf.j2',
            'efs_mount_target': 'aws/storage/efs_mount_target.tf.j2',
            'efs_access_point': 'aws/storage/efs_access_point.tf.j2',

            # Add template mappings
            'elbv2_listener_rule': 'aws/networking/elbv2_listener_rule.tf.j2',
            'elbv2_ssl_policy_reference': 'aws/networking/elbv2_ssl_policy_reference.tf.j2',
            'cloudfront_distribution': 'aws/cdn/cloudfront_distribution.tf.j2',
            'cloudfront_origin_access_control': 'aws/cdn/cloudfront_origin_access_control.tf.j2',
            'cloudfront_cache_policy': 'aws/cdn/cloudfront_cache_policy.tf.j2',
            'cloudfront_origin_request_policy': 'aws/cdn/cloudfront_origin_request_policy.tf.j2',

            # AWS Caching (ElastiCache)
            'elasticache_replication_group': 'aws/caching/elasticache_replication_group.tf.j2',
            'elasticache_redis_cluster': 'aws/caching/elasticache_redis_cluster.tf.j2',
            'elasticache_memcached_cluster': 'aws/caching/elasticache_memcached_cluster.tf.j2',
            'elasticache_subnet_group': 'aws/caching/elasticache_subnet_group.tf.j2',
            'elasticache_parameter_group': 'aws/caching/elasticache_parameter_group.tf.j2',

           # AWS Messaging
            'sqs_queue': 'aws/messaging/sqs_queue.tf.j2',
            'sqs_dlq_relationship': 'aws/messaging/sqs_dlq_relationship.tf.j2',
            'sns_topic': 'aws/messaging/sns_topic.tf.j2',
            'sns_subscription': 'aws/messaging/sns_subscription.tf.j2',
            
            # AWS Secrets & Systems Management
            'secretsmanager_secret': 'aws/security/secretsmanager_secret.tf.j2',
            'secretsmanager_secret_version': 'aws/security/secretsmanager_secret_version.tf.j2',
            'ssm_parameter': 'aws/management/ssm_parameter.tf.j2',
            'ssm_document': 'aws/management/ssm_document.tf.j2',
            'ssm_maintenance_window': 'aws/management/ssm_maintenance_window.tf.j2',

            # In template_mapping dict, add:
            'gcp_instance': 'gcp/compute/gcp_instance.tf.j2',
            'gcp_disk': 'gcp/compute/gcp_disk.tf.j2',
            'gcp_network': 'gcp/network/gcp_network.tf.j2',
            'gcp_subnet': 'gcp/network/gcp_subnet.tf.j2',
            'gcp_firewall': 'gcp/network/gcp_firewall.tf.j2',
            'gcp_bucket': 'gcp/storage/gcp_bucket.tf.j2',
        }
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape()
        )

    def get_template_path(self, resource_type: str, provider: str = 'aws') -> str:
        """Get template path with provider support and backward compatibility"""
        
        # 1. Check for direct mapping first (backward compatibility)
        if resource_type in self.template_mapping:
            template_path = self.template_mapping[resource_type]
            if (self.template_dir / template_path).exists():
                return template_path
        
        # 2. Try provider-specific path
        provider_path = f"{provider}/{resource_type}.tf.j2"
        if (self.template_dir / provider_path).exists():
            return provider_path
        
        # 3. Try category-based search (ADDED 'cdn' to categories)
        categories = ['compute', 'storage', 'database', 'networking', 'dns', 'security', 'integration', 'serverless', 'monitoring', 'cdn']
        for category in categories:
            category_path = f"{provider}/{category}/{resource_type}.tf.j2"
            if (self.template_dir / category_path).exists():
                return category_path
        
        # 4. Fallback to old flat structure (for transition period)
        legacy_path = f"{resource_type}.tf.j2"
        if (self.template_dir / legacy_path).exists():
            return legacy_path
        
        # 5. If nothing found, raise error
        raise FileNotFoundError(f"Template not found for {resource_type} (provider: {provider})")

    def render_template(self, resource_type: str, resources: list, provider: str = 'aws') -> str:
        """Render template with resources"""
        template_path = self.get_template_path(resource_type, provider)
        template = self.env.get_template(template_path)
        return template.render(resources=resources)

    def list_available_templates(self, provider: str = 'aws') -> dict:
        """List all available templates for a provider"""
        provider_dir = self.template_dir / provider
        if not provider_dir.exists():
            return {}
        
        templates = {}
        for category_dir in provider_dir.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                templates[category_name] = []
                
                for template_file in category_dir.glob('*.tf.j2'):
                    template_name = template_file.stem.replace('.tf', '')
                    templates[category_name].append(template_name)
        
        return templates

# Global instance for backward compatibility
_loader = None

def get_template_loader():
    """Get the global template loader instance"""
    global _loader
    if _loader is None:
        _loader = MultiCloudTemplateLoader()
    return _loader

# Updated generate_tf function with backward compatibility
def generate_tf(resources, resource_type: str, output_path: Path, provider: str = 'aws'):
    """Generate Terraform file with multi-cloud support"""
    loader = get_template_loader()
    tf_output = loader.render_template(resource_type, resources, provider)
    
    with open(output_path, "w") as f:
        f.write(tf_output)