r'''
# Must CDK for common pattern
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_apigatewayv2 as _aws_cdk_aws_apigatewayv2_ceddda9d
import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_codedeploy as _aws_cdk_aws_codedeploy_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class ApiGatewayFactory(
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.ApiGatewayFactory",
):
    '''Factory class for common API Gateway patterns.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="createManualRoutesApi")
    @builtins.classmethod
    def create_manual_routes_api(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        primary_lambda: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        routes: typing.Sequence[typing.Union["CustomRoute", typing.Dict[builtins.str, typing.Any]]],
        domain_name: typing.Optional[builtins.str] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    ) -> "ApiGatewayToLambda":
        '''Create a manual routes API with common defaults.

        :param scope: -
        :param id: -
        :param primary_lambda: -
        :param routes: -
        :param domain_name: -
        :param hosted_zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555ffb93a752d3507f1c9ea6538d8bcafbb2b5de049cd805d9bbc204e58dbc5d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument primary_lambda", value=primary_lambda, expected_type=type_hints["primary_lambda"])
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        return typing.cast("ApiGatewayToLambda", jsii.sinvoke(cls, "createManualRoutesApi", [scope, id, primary_lambda, routes, domain_name, hosted_zone]))

    @jsii.member(jsii_name="createRoute")
    @builtins.classmethod
    def create_route(
        cls,
        path: builtins.str,
        method: builtins.str,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        require_api_key: typing.Optional[builtins.bool] = None,
    ) -> "CustomRoute":
        '''Helper to create CustomRoute with API key requirement.

        :param path: -
        :param method: -
        :param handler: -
        :param require_api_key: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f908752c820c2520d96e5a971a226d517cd27118bae48a36f2ad9b8a840d4706)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument require_api_key", value=require_api_key, expected_type=type_hints["require_api_key"])
        return typing.cast("CustomRoute", jsii.sinvoke(cls, "createRoute", [path, method, handler, require_api_key]))

    @jsii.member(jsii_name="createSimpleProxyApi")
    @builtins.classmethod
    def create_simple_proxy_api(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        domain_name: typing.Optional[builtins.str] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    ) -> "ApiGatewayToLambda":
        '''Create a simple proxy API with common defaults.

        :param scope: -
        :param id: -
        :param lambda_function: -
        :param domain_name: -
        :param hosted_zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__512566c18e3ea9319fce8a6031ac1d18fc51efeef4dc266b9836690386421057)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        return typing.cast("ApiGatewayToLambda", jsii.sinvoke(cls, "createSimpleProxyApi", [scope, id, lambda_function, domain_name, hosted_zone]))


class ApiGatewayToLambda(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.ApiGatewayToLambda",
):
    '''Enhanced API Gateway to Lambda construct supporting both proxy and manual routing.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_gateway: typing.Union["ApiProps", typing.Dict[builtins.str, typing.Any]],
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        certificate_arn: typing.Optional[builtins.str] = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        custom_routes: typing.Optional[typing.Sequence[typing.Union["CustomRoute", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_gateway: API configuration.
        :param lambda_function: Primary Lambda function for the API.
        :param certificate_arn: Optional ACM certificate ARN to use instead of creating a new one.
        :param create_usage_plan: Whether to create a Usage Plan.
        :param custom_domain_name: Optional custom domain name for API Gateway.
        :param custom_routes: Custom routes for manual API setup (when proxy is false) If provided, will use RestApi instead of LambdaRestApi.
        :param enable_logging: Enable CloudWatch logging for API Gateway.
        :param hosted_zone: Optional Route53 hosted zone for custom domain.
        :param log_group_props: CloudWatch Logs configuration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88385340a9ac0a3d345bb5f8b9e0334655a117a97d92f90c383b720f4bbd4824)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiGatewayToLambdaProps(
            api_gateway=api_gateway,
            lambda_function=lambda_function,
            certificate_arn=certificate_arn,
            create_usage_plan=create_usage_plan,
            custom_domain_name=custom_domain_name,
            custom_routes=custom_routes,
            enable_logging=enable_logging,
            hosted_zone=hosted_zone,
            log_group_props=log_group_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRoute")
    def add_route(
        self,
        *,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        method: builtins.str,
        path: builtins.str,
        method_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> _aws_cdk_aws_apigateway_ceddda9d.Method:
        '''Add a custom route after construction (for dynamic route addition).

        :param handler: 
        :param method: 
        :param path: 
        :param method_options: 
        '''
        route = CustomRoute(
            handler=handler, method=method, path=path, method_options=method_options
        )

        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.Method, jsii.invoke(self, "addRoute", [route]))

    @builtins.property
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property
    @jsii.member(jsii_name="apiUrl")
    def api_url(self) -> builtins.str:
        '''Get the API Gateway URL (useful for outputs).'''
        return typing.cast(builtins.str, jsii.get(self, "apiUrl"))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroup], jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="aRecord")
    def a_record(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord]:
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord], jsii.get(self, "aRecord"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainName]:
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.DomainName], jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="usagePlan")
    def usage_plan(self) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.UsagePlan]:
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.UsagePlan], jsii.get(self, "usagePlan"))


@jsii.data_type(
    jsii_type="must-cdk.ApiGatewayToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_gateway": "apiGateway",
        "lambda_function": "lambdaFunction",
        "certificate_arn": "certificateArn",
        "create_usage_plan": "createUsagePlan",
        "custom_domain_name": "customDomainName",
        "custom_routes": "customRoutes",
        "enable_logging": "enableLogging",
        "hosted_zone": "hostedZone",
        "log_group_props": "logGroupProps",
    },
)
class ApiGatewayToLambdaProps:
    def __init__(
        self,
        *,
        api_gateway: typing.Union["ApiProps", typing.Dict[builtins.str, typing.Any]],
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        certificate_arn: typing.Optional[builtins.str] = None,
        create_usage_plan: typing.Optional[builtins.bool] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        custom_routes: typing.Optional[typing.Sequence[typing.Union["CustomRoute", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_gateway: API configuration.
        :param lambda_function: Primary Lambda function for the API.
        :param certificate_arn: Optional ACM certificate ARN to use instead of creating a new one.
        :param create_usage_plan: Whether to create a Usage Plan.
        :param custom_domain_name: Optional custom domain name for API Gateway.
        :param custom_routes: Custom routes for manual API setup (when proxy is false) If provided, will use RestApi instead of LambdaRestApi.
        :param enable_logging: Enable CloudWatch logging for API Gateway.
        :param hosted_zone: Optional Route53 hosted zone for custom domain.
        :param log_group_props: CloudWatch Logs configuration.
        '''
        if isinstance(api_gateway, dict):
            api_gateway = ApiProps(**api_gateway)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c51143b7da8fc50ffd3240aae88642c332f9ccc1136e275abf9d1065df7ea17)
            check_type(argname="argument api_gateway", value=api_gateway, expected_type=type_hints["api_gateway"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument certificate_arn", value=certificate_arn, expected_type=type_hints["certificate_arn"])
            check_type(argname="argument create_usage_plan", value=create_usage_plan, expected_type=type_hints["create_usage_plan"])
            check_type(argname="argument custom_domain_name", value=custom_domain_name, expected_type=type_hints["custom_domain_name"])
            check_type(argname="argument custom_routes", value=custom_routes, expected_type=type_hints["custom_routes"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_gateway": api_gateway,
            "lambda_function": lambda_function,
        }
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if create_usage_plan is not None:
            self._values["create_usage_plan"] = create_usage_plan
        if custom_domain_name is not None:
            self._values["custom_domain_name"] = custom_domain_name
        if custom_routes is not None:
            self._values["custom_routes"] = custom_routes
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props

    @builtins.property
    def api_gateway(self) -> "ApiProps":
        '''API configuration.'''
        result = self._values.get("api_gateway")
        assert result is not None, "Required property 'api_gateway' is missing"
        return typing.cast("ApiProps", result)

    @builtins.property
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''Primary Lambda function for the API.'''
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Optional ACM certificate ARN to use instead of creating a new one.'''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_usage_plan(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a Usage Plan.'''
        result = self._values.get("create_usage_plan")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_domain_name(self) -> typing.Optional[builtins.str]:
        '''Optional custom domain name for API Gateway.'''
        result = self._values.get("custom_domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_routes(self) -> typing.Optional[typing.List["CustomRoute"]]:
        '''Custom routes for manual API setup (when proxy is false) If provided, will use RestApi instead of LambdaRestApi.'''
        result = self._values.get("custom_routes")
        return typing.cast(typing.Optional[typing.List["CustomRoute"]], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable CloudWatch logging for API Gateway.'''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''Optional Route53 hosted zone for custom domain.'''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def log_group_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps]:
        '''CloudWatch Logs configuration.'''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.ApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_name": "apiName",
        "lambda_api_props": "lambdaApiProps",
        "proxy": "proxy",
        "rest_api_props": "restApiProps",
    },
)
class ApiProps:
    def __init__(
        self,
        *,
        api_name: builtins.str,
        lambda_api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.LambdaRestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
        proxy: typing.Optional[builtins.bool] = None,
        rest_api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_name: 
        :param lambda_api_props: 
        :param proxy: 
        :param rest_api_props: 
        '''
        if isinstance(lambda_api_props, dict):
            lambda_api_props = _aws_cdk_aws_apigateway_ceddda9d.LambdaRestApiProps(**lambda_api_props)
        if isinstance(rest_api_props, dict):
            rest_api_props = _aws_cdk_aws_apigateway_ceddda9d.RestApiProps(**rest_api_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b97171af667de8a26858df1339c97d506d81da9dd597dd76896abec03c25e8f4)
            check_type(argname="argument api_name", value=api_name, expected_type=type_hints["api_name"])
            check_type(argname="argument lambda_api_props", value=lambda_api_props, expected_type=type_hints["lambda_api_props"])
            check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
            check_type(argname="argument rest_api_props", value=rest_api_props, expected_type=type_hints["rest_api_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_name": api_name,
        }
        if lambda_api_props is not None:
            self._values["lambda_api_props"] = lambda_api_props
        if proxy is not None:
            self._values["proxy"] = proxy
        if rest_api_props is not None:
            self._values["rest_api_props"] = rest_api_props

    @builtins.property
    def api_name(self) -> builtins.str:
        result = self._values.get("api_name")
        assert result is not None, "Required property 'api_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_api_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.LambdaRestApiProps]:
        result = self._values.get("lambda_api_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.LambdaRestApiProps], result)

    @builtins.property
    def proxy(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("proxy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rest_api_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps]:
        result = self._values.get("rest_api_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.AutoScalingProps",
    jsii_struct_bases=[],
    name_mapping={
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
        "cpu_scale": "cpuScale",
        "memory_scale": "memoryScale",
    },
)
class AutoScalingProps:
    def __init__(
        self,
        *,
        max_capacity: jsii.Number,
        min_capacity: jsii.Number,
        cpu_scale: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CpuUtilizationScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
        memory_scale: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.MemoryUtilizationScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Configuration for ECS service auto-scaling.

        :param max_capacity: Maximum number of tasks to run.
        :param min_capacity: Minimum number of tasks to run.
        :param cpu_scale: Scale task based on CPU utilization.
        :param memory_scale: Scale task based on memory utilization.
        '''
        if isinstance(cpu_scale, dict):
            cpu_scale = _aws_cdk_aws_ecs_ceddda9d.CpuUtilizationScalingProps(**cpu_scale)
        if isinstance(memory_scale, dict):
            memory_scale = _aws_cdk_aws_ecs_ceddda9d.MemoryUtilizationScalingProps(**memory_scale)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0ea30b15daf73de785b4991457443ee0ca220224fbd08155a17d86c67413930)
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
            check_type(argname="argument cpu_scale", value=cpu_scale, expected_type=type_hints["cpu_scale"])
            check_type(argname="argument memory_scale", value=memory_scale, expected_type=type_hints["memory_scale"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_capacity": max_capacity,
            "min_capacity": min_capacity,
        }
        if cpu_scale is not None:
            self._values["cpu_scale"] = cpu_scale
        if memory_scale is not None:
            self._values["memory_scale"] = memory_scale

    @builtins.property
    def max_capacity(self) -> jsii.Number:
        '''Maximum number of tasks to run.'''
        result = self._values.get("max_capacity")
        assert result is not None, "Required property 'max_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_capacity(self) -> jsii.Number:
        '''Minimum number of tasks to run.'''
        result = self._values.get("min_capacity")
        assert result is not None, "Required property 'min_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_scale(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CpuUtilizationScalingProps]:
        '''Scale task based on CPU utilization.'''
        result = self._values.get("cpu_scale")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.CpuUtilizationScalingProps], result)

    @builtins.property
    def memory_scale(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.MemoryUtilizationScalingProps]:
        '''Scale task based on memory utilization.'''
        result = self._values.get("memory_scale")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.MemoryUtilizationScalingProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.ContainerProps",
    jsii_struct_bases=[],
    name_mapping={
        "container_port": "containerPort",
        "image": "image",
        "health_check": "healthCheck",
        "memory_limit": "memoryLimit",
        "memory_reservation": "memoryReservation",
    },
)
class ContainerProps:
    def __init__(
        self,
        *,
        container_port: jsii.Number,
        image: _aws_cdk_aws_ecs_ceddda9d.ContainerImage,
        health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Configuration for the ECS Fargate task definition and container.

        :param container_port: The port number the container listens on.
        :param image: Container image to deploy.
        :param health_check: Optional container health check configuration.
        :param memory_limit: Hard memory limit in MiB for the task (default: 2048).
        :param memory_reservation: Soft memory reservation in MiB for the container (default: 1024).
        '''
        if isinstance(health_check, dict):
            health_check = _aws_cdk_aws_ecs_ceddda9d.HealthCheck(**health_check)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54ea2679bab87dfe8eb538ebc455f8d93200c1beb37ad6e093fa52678f8ac1fc)
            check_type(argname="argument container_port", value=container_port, expected_type=type_hints["container_port"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument memory_limit", value=memory_limit, expected_type=type_hints["memory_limit"])
            check_type(argname="argument memory_reservation", value=memory_reservation, expected_type=type_hints["memory_reservation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container_port": container_port,
            "image": image,
        }
        if health_check is not None:
            self._values["health_check"] = health_check
        if memory_limit is not None:
            self._values["memory_limit"] = memory_limit
        if memory_reservation is not None:
            self._values["memory_reservation"] = memory_reservation

    @builtins.property
    def container_port(self) -> jsii.Number:
        '''The port number the container listens on.'''
        result = self._values.get("container_port")
        assert result is not None, "Required property 'container_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def image(self) -> _aws_cdk_aws_ecs_ceddda9d.ContainerImage:
        '''Container image to deploy.'''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ContainerImage, result)

    @builtins.property
    def health_check(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck]:
        '''Optional container health check configuration.'''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.HealthCheck], result)

    @builtins.property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        '''Hard memory limit in MiB for the task (default: 2048).'''
        result = self._values.get("memory_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_reservation(self) -> typing.Optional[jsii.Number]:
        '''Soft memory reservation in MiB for the container (default: 1024).'''
        result = self._values.get("memory_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.CustomRoute",
    jsii_struct_bases=[],
    name_mapping={
        "handler": "handler",
        "method": "method",
        "path": "path",
        "method_options": "methodOptions",
    },
)
class CustomRoute:
    def __init__(
        self,
        *,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        method: builtins.str,
        path: builtins.str,
        method_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param handler: 
        :param method: 
        :param path: 
        :param method_options: 
        '''
        if isinstance(method_options, dict):
            method_options = _aws_cdk_aws_apigateway_ceddda9d.MethodOptions(**method_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__037506344a4229895450ab2466c4a39abd0da2085c3a5d744bc1a0bdaf3a2c8d)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument method_options", value=method_options, expected_type=type_hints["method_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "handler": handler,
            "method": method,
            "path": path,
        }
        if method_options is not None:
            self._values["method_options"] = method_options

    @builtins.property
    def handler(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def method(self) -> builtins.str:
        result = self._values.get("method")
        assert result is not None, "Required property 'method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions]:
        result = self._values.get("method_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomRoute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcsCodeDeploy(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.EcsCodeDeploy",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        containers: typing.Sequence[typing.Union[ContainerProps, typing.Dict[builtins.str, typing.Any]]],
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        service_name: builtins.str,
        subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        alb_target_port: typing.Optional[jsii.Number] = None,
        auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_public_load_balancer: typing.Optional[builtins.bool] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        task_cpu: typing.Optional[jsii.Number] = None,
        task_exec_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        task_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificates: Optional ACM certificates for HTTPS termination.
        :param cluster: ECS Cluster where the service will run.
        :param containers: Configuration related to the task definition and container.
        :param security_groups: Security group config.
        :param service_name: Base name used for resources like log groups, roles, services, etc.
        :param subnets: Select which subnets the Service and ALB will placed on.
        :param vpc: VPC in which to deploy ECS and ALB resources.
        :param alb_target_port: The ALB target port.
        :param auto_scaling: Optional auto-scaling configuration.
        :param enable_public_load_balancer: Whether the load balancer should be internet-facing (default: false).
        :param memory_limit: 
        :param task_cpu: CPU units for the task (default: 1024).
        :param task_exec_role: Task execution role for the ECS task.
        :param task_role: Task role for the ECS task.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19ac4f77d3bba1391929b87d2d23b70fe61e21aa6809f43ed4283d6ecf350909)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EcsCodeDeployProps(
            certificates=certificates,
            cluster=cluster,
            containers=containers,
            security_groups=security_groups,
            service_name=service_name,
            subnets=subnets,
            vpc=vpc,
            alb_target_port=alb_target_port,
            auto_scaling=auto_scaling,
            enable_public_load_balancer=enable_public_load_balancer,
            memory_limit=memory_limit,
            task_cpu=task_cpu,
            task_exec_role=task_exec_role,
            task_role=task_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allListeners")
    def all_listeners(
        self,
    ) -> typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener]:
        return typing.cast(typing.List[_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener], jsii.invoke(self, "allListeners", []))

    @jsii.member(jsii_name="blueListener")
    def blue_listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener, jsii.invoke(self, "blueListener", []))

    @jsii.member(jsii_name="greenListener")
    def green_listener(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationListener, jsii.invoke(self, "greenListener", []))

    @jsii.member(jsii_name="loadBalancerDnsName")
    def load_balancer_dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "loadBalancerDnsName", []))

    @jsii.member(jsii_name="serviceArn")
    def service_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "serviceArn", []))

    @builtins.property
    @jsii.member(jsii_name="blueTargetGroup")
    def blue_target_group(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup, jsii.get(self, "blueTargetGroup"))

    @builtins.property
    @jsii.member(jsii_name="codeDeployApp")
    def code_deploy_app(self) -> _aws_cdk_aws_codedeploy_ceddda9d.EcsApplication:
        return typing.cast(_aws_cdk_aws_codedeploy_ceddda9d.EcsApplication, jsii.get(self, "codeDeployApp"))

    @builtins.property
    @jsii.member(jsii_name="greenTargetGroup")
    def green_target_group(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationTargetGroup, jsii.get(self, "greenTargetGroup"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> _aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer:
        return typing.cast(_aws_cdk_aws_elasticloadbalancingv2_ceddda9d.ApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.FargateService:
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.FargateService, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="taskDef")
    def task_def(self) -> _aws_cdk_aws_ecs_ceddda9d.TaskDefinition:
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.TaskDefinition, jsii.get(self, "taskDef"))

    @builtins.property
    @jsii.member(jsii_name="taskExecutionRole")
    def task_execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "taskExecutionRole"))

    @builtins.property
    @jsii.member(jsii_name="taskRole")
    def task_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "taskRole"))


@jsii.data_type(
    jsii_type="must-cdk.EcsCodeDeployProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificates": "certificates",
        "cluster": "cluster",
        "containers": "containers",
        "security_groups": "securityGroups",
        "service_name": "serviceName",
        "subnets": "subnets",
        "vpc": "vpc",
        "alb_target_port": "albTargetPort",
        "auto_scaling": "autoScaling",
        "enable_public_load_balancer": "enablePublicLoadBalancer",
        "memory_limit": "memoryLimit",
        "task_cpu": "taskCPU",
        "task_exec_role": "taskExecRole",
        "task_role": "taskRole",
    },
)
class EcsCodeDeployProps:
    def __init__(
        self,
        *,
        certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        containers: typing.Sequence[typing.Union[ContainerProps, typing.Dict[builtins.str, typing.Any]]],
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        service_name: builtins.str,
        subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        alb_target_port: typing.Optional[jsii.Number] = None,
        auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_public_load_balancer: typing.Optional[builtins.bool] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        task_cpu: typing.Optional[jsii.Number] = None,
        task_exec_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        task_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''Properties for the EcsCodeDeploy construct.

        :param certificates: Optional ACM certificates for HTTPS termination.
        :param cluster: ECS Cluster where the service will run.
        :param containers: Configuration related to the task definition and container.
        :param security_groups: Security group config.
        :param service_name: Base name used for resources like log groups, roles, services, etc.
        :param subnets: Select which subnets the Service and ALB will placed on.
        :param vpc: VPC in which to deploy ECS and ALB resources.
        :param alb_target_port: The ALB target port.
        :param auto_scaling: Optional auto-scaling configuration.
        :param enable_public_load_balancer: Whether the load balancer should be internet-facing (default: false).
        :param memory_limit: 
        :param task_cpu: CPU units for the task (default: 1024).
        :param task_exec_role: Task execution role for the ECS task.
        :param task_role: Task role for the ECS task.
        '''
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if isinstance(auto_scaling, dict):
            auto_scaling = AutoScalingProps(**auto_scaling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e1edfc306738ea99e0bd03a55876d7f75a063970dd3103fc1bbb766dff014b1)
            check_type(argname="argument certificates", value=certificates, expected_type=type_hints["certificates"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument containers", value=containers, expected_type=type_hints["containers"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument alb_target_port", value=alb_target_port, expected_type=type_hints["alb_target_port"])
            check_type(argname="argument auto_scaling", value=auto_scaling, expected_type=type_hints["auto_scaling"])
            check_type(argname="argument enable_public_load_balancer", value=enable_public_load_balancer, expected_type=type_hints["enable_public_load_balancer"])
            check_type(argname="argument memory_limit", value=memory_limit, expected_type=type_hints["memory_limit"])
            check_type(argname="argument task_cpu", value=task_cpu, expected_type=type_hints["task_cpu"])
            check_type(argname="argument task_exec_role", value=task_exec_role, expected_type=type_hints["task_exec_role"])
            check_type(argname="argument task_role", value=task_role, expected_type=type_hints["task_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificates": certificates,
            "cluster": cluster,
            "containers": containers,
            "security_groups": security_groups,
            "service_name": service_name,
            "subnets": subnets,
            "vpc": vpc,
        }
        if alb_target_port is not None:
            self._values["alb_target_port"] = alb_target_port
        if auto_scaling is not None:
            self._values["auto_scaling"] = auto_scaling
        if enable_public_load_balancer is not None:
            self._values["enable_public_load_balancer"] = enable_public_load_balancer
        if memory_limit is not None:
            self._values["memory_limit"] = memory_limit
        if task_cpu is not None:
            self._values["task_cpu"] = task_cpu
        if task_exec_role is not None:
            self._values["task_exec_role"] = task_exec_role
        if task_role is not None:
            self._values["task_role"] = task_role

    @builtins.property
    def certificates(
        self,
    ) -> typing.List[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        '''Optional ACM certificates for HTTPS termination.'''
        result = self._values.get("certificates")
        assert result is not None, "Required property 'certificates' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], result)

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''ECS Cluster where the service will run.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def containers(self) -> typing.List[ContainerProps]:
        '''Configuration related to the task definition and container.'''
        result = self._values.get("containers")
        assert result is not None, "Required property 'containers' is missing"
        return typing.cast(typing.List[ContainerProps], result)

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security group config.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''Base name used for resources like log groups, roles, services, etc.'''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnets(self) -> _aws_cdk_aws_ec2_ceddda9d.SubnetSelection:
        '''Select which subnets the Service and ALB will placed on.'''
        result = self._values.get("subnets")
        assert result is not None, "Required property 'subnets' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC in which to deploy ECS and ALB resources.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def alb_target_port(self) -> typing.Optional[jsii.Number]:
        '''The ALB target port.'''
        result = self._values.get("alb_target_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def auto_scaling(self) -> typing.Optional[AutoScalingProps]:
        '''Optional auto-scaling configuration.'''
        result = self._values.get("auto_scaling")
        return typing.cast(typing.Optional[AutoScalingProps], result)

    @builtins.property
    def enable_public_load_balancer(self) -> typing.Optional[builtins.bool]:
        '''Whether the load balancer should be internet-facing (default: false).'''
        result = self._values.get("enable_public_load_balancer")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("memory_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def task_cpu(self) -> typing.Optional[jsii.Number]:
        '''CPU units for the task (default: 1024).'''
        result = self._values.get("task_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def task_exec_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Task execution role for the ECS task.'''
        result = self._values.get("task_exec_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def task_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''Task role for the ECS task.'''
        result = self._values.get("task_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsCodeDeployProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebSocketApiGatewayFactory(
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.WebSocketApiGatewayFactory",
):
    '''Factory class for common WebSocket API Gateway patterns.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="createCommonRoutes")
    @builtins.classmethod
    def create_common_routes(
        cls,
        connect_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        disconnect_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        default_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> typing.List["WebSocketRoute"]:
        '''Create common WebSocket routes (connect, disconnect, default).

        :param connect_handler: -
        :param disconnect_handler: -
        :param default_handler: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c063f743e1f72b467dbd5e3c1b50e12ced31a4dc57d989ab67b5420ebfa12ce)
            check_type(argname="argument connect_handler", value=connect_handler, expected_type=type_hints["connect_handler"])
            check_type(argname="argument disconnect_handler", value=disconnect_handler, expected_type=type_hints["disconnect_handler"])
            check_type(argname="argument default_handler", value=default_handler, expected_type=type_hints["default_handler"])
        return typing.cast(typing.List["WebSocketRoute"], jsii.sinvoke(cls, "createCommonRoutes", [connect_handler, disconnect_handler, default_handler]))

    @jsii.member(jsii_name="createRoute")
    @builtins.classmethod
    def create_route(
        cls,
        route_key: builtins.str,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        route_response_selection_expression: typing.Optional[builtins.str] = None,
    ) -> "WebSocketRoute":
        '''Helper to create WebSocket route.

        :param route_key: -
        :param handler: -
        :param route_response_selection_expression: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__086f4831c9bd7268c4a6f1ebbd644aefacbb7ff7cc1b52e6393dcd78ac290b95)
            check_type(argname="argument route_key", value=route_key, expected_type=type_hints["route_key"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument route_response_selection_expression", value=route_response_selection_expression, expected_type=type_hints["route_response_selection_expression"])
        return typing.cast("WebSocketRoute", jsii.sinvoke(cls, "createRoute", [route_key, handler, route_response_selection_expression]))

    @jsii.member(jsii_name="createSimpleWebSocketApi")
    @builtins.classmethod
    def create_simple_web_socket_api(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        domain_name: typing.Optional[builtins.str] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    ) -> "WebSocketApiGatewayToLambda":
        '''Create a simple WebSocket API with common defaults.

        :param scope: -
        :param id: -
        :param lambda_function: -
        :param domain_name: -
        :param hosted_zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18bbe2305cfca74cc21cbc3685c858f68a283a4e8175a04cb1f1cfceee1d48e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        return typing.cast("WebSocketApiGatewayToLambda", jsii.sinvoke(cls, "createSimpleWebSocketApi", [scope, id, lambda_function, domain_name, hosted_zone]))

    @jsii.member(jsii_name="createWebSocketApiWithRoutes")
    @builtins.classmethod
    def create_web_socket_api_with_routes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        default_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        routes: typing.Sequence[typing.Union["WebSocketRoute", typing.Dict[builtins.str, typing.Any]]],
        domain_name: typing.Optional[builtins.str] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    ) -> "WebSocketApiGatewayToLambda":
        '''Create a WebSocket API with custom routes.

        :param scope: -
        :param id: -
        :param default_handler: -
        :param routes: -
        :param domain_name: -
        :param hosted_zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ef8aa08462eac4d715eed8d4ba1eebf11c6b448eaa5babff0820753e58341bf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument default_handler", value=default_handler, expected_type=type_hints["default_handler"])
            check_type(argname="argument routes", value=routes, expected_type=type_hints["routes"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
        return typing.cast("WebSocketApiGatewayToLambda", jsii.sinvoke(cls, "createWebSocketApiWithRoutes", [scope, id, default_handler, routes, domain_name, hosted_zone]))


class WebSocketApiGatewayToLambda(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="must-cdk.WebSocketApiGatewayToLambda",
):
    '''Enhanced WebSocket API Gateway to Lambda construct.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        web_socket_api: typing.Union["WebSocketApiProps", typing.Dict[builtins.str, typing.Any]],
        certificate_arn: typing.Optional[builtins.str] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        custom_routes: typing.Optional[typing.Sequence[typing.Union["WebSocketRoute", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lambda_function: Primary Lambda function for the API (usually handles $default route).
        :param web_socket_api: WebSocket API configuration.
        :param certificate_arn: Optional ACM certificate ARN to use instead of creating a new one.
        :param custom_domain_name: Optional custom domain name for API Gateway.
        :param custom_routes: Custom routes for WebSocket API Common routes: $connect, $disconnect, $default, or custom route keys.
        :param enable_logging: Enable CloudWatch logging for API Gateway.
        :param hosted_zone: Optional Route53 hosted zone for custom domain.
        :param log_group_props: CloudWatch Logs configuration.
        :param stage_name: Stage name for the WebSocket API. Default: 'dev'
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15689bf8cb45b613fd6d0271ea2d2b2a40c677ff7ee1d37b34596aa645c185e9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WebSocketApiGatewayToLambdaProps(
            lambda_function=lambda_function,
            web_socket_api=web_socket_api,
            certificate_arn=certificate_arn,
            custom_domain_name=custom_domain_name,
            custom_routes=custom_routes,
            enable_logging=enable_logging,
            hosted_zone=hosted_zone,
            log_group_props=log_group_props,
            stage_name=stage_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRoute")
    def add_route(
        self,
        *,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        route_key: builtins.str,
        route_response_selection_expression: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketRoute:
        '''Add a custom route after construction (for dynamic route addition).

        :param handler: 
        :param route_key: 
        :param route_response_selection_expression: 
        '''
        route = WebSocketRoute(
            handler=handler,
            route_key=route_key,
            route_response_selection_expression=route_response_selection_expression,
        )

        return typing.cast(_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketRoute, jsii.invoke(self, "addRoute", [route]))

    @builtins.property
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, jsii.get(self, "lambdaFunction"))

    @builtins.property
    @jsii.member(jsii_name="webSocketApi")
    def web_socket_api(self) -> _aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApi:
        return typing.cast(_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApi, jsii.get(self, "webSocketApi"))

    @builtins.property
    @jsii.member(jsii_name="webSocketStage")
    def web_socket_stage(self) -> _aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketStage:
        return typing.cast(_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketStage, jsii.get(self, "webSocketStage"))

    @builtins.property
    @jsii.member(jsii_name="webSocketUrl")
    def web_socket_url(self) -> builtins.str:
        '''Get the WebSocket API URL (useful for outputs).'''
        return typing.cast(builtins.str, jsii.get(self, "webSocketUrl"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], jsii.get(self, "apiGatewayCloudWatchRole"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroup]:
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroup], jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property
    @jsii.member(jsii_name="aRecord")
    def a_record(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord]:
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.ARecord], jsii.get(self, "aRecord"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate]:
        return typing.cast(typing.Optional[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate], jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[_aws_cdk_aws_apigatewayv2_ceddda9d.DomainName]:
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_ceddda9d.DomainName], jsii.get(self, "domain"))


@jsii.data_type(
    jsii_type="must-cdk.WebSocketApiGatewayToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "lambda_function": "lambdaFunction",
        "web_socket_api": "webSocketApi",
        "certificate_arn": "certificateArn",
        "custom_domain_name": "customDomainName",
        "custom_routes": "customRoutes",
        "enable_logging": "enableLogging",
        "hosted_zone": "hostedZone",
        "log_group_props": "logGroupProps",
        "stage_name": "stageName",
    },
)
class WebSocketApiGatewayToLambdaProps:
    def __init__(
        self,
        *,
        lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        web_socket_api: typing.Union["WebSocketApiProps", typing.Dict[builtins.str, typing.Any]],
        certificate_arn: typing.Optional[builtins.str] = None,
        custom_domain_name: typing.Optional[builtins.str] = None,
        custom_routes: typing.Optional[typing.Sequence[typing.Union["WebSocketRoute", typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
        log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
        stage_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param lambda_function: Primary Lambda function for the API (usually handles $default route).
        :param web_socket_api: WebSocket API configuration.
        :param certificate_arn: Optional ACM certificate ARN to use instead of creating a new one.
        :param custom_domain_name: Optional custom domain name for API Gateway.
        :param custom_routes: Custom routes for WebSocket API Common routes: $connect, $disconnect, $default, or custom route keys.
        :param enable_logging: Enable CloudWatch logging for API Gateway.
        :param hosted_zone: Optional Route53 hosted zone for custom domain.
        :param log_group_props: CloudWatch Logs configuration.
        :param stage_name: Stage name for the WebSocket API. Default: 'dev'
        '''
        if isinstance(web_socket_api, dict):
            web_socket_api = WebSocketApiProps(**web_socket_api)
        if isinstance(log_group_props, dict):
            log_group_props = _aws_cdk_aws_logs_ceddda9d.LogGroupProps(**log_group_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63f4cdf57fbe667cd56ca0962570b3a041ac0113f05528d7f2964cb201e11e6e)
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
            check_type(argname="argument web_socket_api", value=web_socket_api, expected_type=type_hints["web_socket_api"])
            check_type(argname="argument certificate_arn", value=certificate_arn, expected_type=type_hints["certificate_arn"])
            check_type(argname="argument custom_domain_name", value=custom_domain_name, expected_type=type_hints["custom_domain_name"])
            check_type(argname="argument custom_routes", value=custom_routes, expected_type=type_hints["custom_routes"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument log_group_props", value=log_group_props, expected_type=type_hints["log_group_props"])
            check_type(argname="argument stage_name", value=stage_name, expected_type=type_hints["stage_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lambda_function": lambda_function,
            "web_socket_api": web_socket_api,
        }
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if custom_domain_name is not None:
            self._values["custom_domain_name"] = custom_domain_name
        if custom_routes is not None:
            self._values["custom_routes"] = custom_routes
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if hosted_zone is not None:
            self._values["hosted_zone"] = hosted_zone
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props
        if stage_name is not None:
            self._values["stage_name"] = stage_name

    @builtins.property
    def lambda_function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''Primary Lambda function for the API (usually handles $default route).'''
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def web_socket_api(self) -> "WebSocketApiProps":
        '''WebSocket API configuration.'''
        result = self._values.get("web_socket_api")
        assert result is not None, "Required property 'web_socket_api' is missing"
        return typing.cast("WebSocketApiProps", result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Optional ACM certificate ARN to use instead of creating a new one.'''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_domain_name(self) -> typing.Optional[builtins.str]:
        '''Optional custom domain name for API Gateway.'''
        result = self._values.get("custom_domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_routes(self) -> typing.Optional[typing.List["WebSocketRoute"]]:
        '''Custom routes for WebSocket API Common routes: $connect, $disconnect, $default, or custom route keys.'''
        result = self._values.get("custom_routes")
        return typing.cast(typing.Optional[typing.List["WebSocketRoute"]], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable CloudWatch logging for API Gateway.'''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def hosted_zone(self) -> typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone]:
        '''Optional Route53 hosted zone for custom domain.'''
        result = self._values.get("hosted_zone")
        return typing.cast(typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone], result)

    @builtins.property
    def log_group_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps]:
        '''CloudWatch Logs configuration.'''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.LogGroupProps], result)

    @builtins.property
    def stage_name(self) -> typing.Optional[builtins.str]:
        '''Stage name for the WebSocket API.

        :default: 'dev'
        '''
        result = self._values.get("stage_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketApiGatewayToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.WebSocketApiProps",
    jsii_struct_bases=[],
    name_mapping={"api_name": "apiName", "api_props": "apiProps"},
)
class WebSocketApiProps:
    def __init__(
        self,
        *,
        api_name: builtins.str,
        api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_name: 
        :param api_props: 
        '''
        if isinstance(api_props, dict):
            api_props = _aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApiProps(**api_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2283390d86917e3d80fc2b4212dba64f234ec0bfdb8a83f8fc6c17d748dc71cc)
            check_type(argname="argument api_name", value=api_name, expected_type=type_hints["api_name"])
            check_type(argname="argument api_props", value=api_props, expected_type=type_hints["api_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_name": api_name,
        }
        if api_props is not None:
            self._values["api_props"] = api_props

    @builtins.property
    def api_name(self) -> builtins.str:
        result = self._values.get("api_name")
        assert result is not None, "Required property 'api_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApiProps]:
        result = self._values.get("api_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApiProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="must-cdk.WebSocketRoute",
    jsii_struct_bases=[],
    name_mapping={
        "handler": "handler",
        "route_key": "routeKey",
        "route_response_selection_expression": "routeResponseSelectionExpression",
    },
)
class WebSocketRoute:
    def __init__(
        self,
        *,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        route_key: builtins.str,
        route_response_selection_expression: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param handler: 
        :param route_key: 
        :param route_response_selection_expression: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34bf0c8251244f50bde7c9d5fe60d88348a1be2cec9ac52b2fae8d7918d72b62)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument route_key", value=route_key, expected_type=type_hints["route_key"])
            check_type(argname="argument route_response_selection_expression", value=route_response_selection_expression, expected_type=type_hints["route_response_selection_expression"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "handler": handler,
            "route_key": route_key,
        }
        if route_response_selection_expression is not None:
            self._values["route_response_selection_expression"] = route_response_selection_expression

    @builtins.property
    def handler(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def route_key(self) -> builtins.str:
        result = self._values.get("route_key")
        assert result is not None, "Required property 'route_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def route_response_selection_expression(self) -> typing.Optional[builtins.str]:
        result = self._values.get("route_response_selection_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebSocketRoute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayFactory",
    "ApiGatewayToLambda",
    "ApiGatewayToLambdaProps",
    "ApiProps",
    "AutoScalingProps",
    "ContainerProps",
    "CustomRoute",
    "EcsCodeDeploy",
    "EcsCodeDeployProps",
    "WebSocketApiGatewayFactory",
    "WebSocketApiGatewayToLambda",
    "WebSocketApiGatewayToLambdaProps",
    "WebSocketApiProps",
    "WebSocketRoute",
]

publication.publish()

def _typecheckingstub__555ffb93a752d3507f1c9ea6538d8bcafbb2b5de049cd805d9bbc204e58dbc5d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    primary_lambda: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    routes: typing.Sequence[typing.Union[CustomRoute, typing.Dict[builtins.str, typing.Any]]],
    domain_name: typing.Optional[builtins.str] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f908752c820c2520d96e5a971a226d517cd27118bae48a36f2ad9b8a840d4706(
    path: builtins.str,
    method: builtins.str,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    require_api_key: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__512566c18e3ea9319fce8a6031ac1d18fc51efeef4dc266b9836690386421057(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    domain_name: typing.Optional[builtins.str] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88385340a9ac0a3d345bb5f8b9e0334655a117a97d92f90c383b720f4bbd4824(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_gateway: typing.Union[ApiProps, typing.Dict[builtins.str, typing.Any]],
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    certificate_arn: typing.Optional[builtins.str] = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    custom_routes: typing.Optional[typing.Sequence[typing.Union[CustomRoute, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c51143b7da8fc50ffd3240aae88642c332f9ccc1136e275abf9d1065df7ea17(
    *,
    api_gateway: typing.Union[ApiProps, typing.Dict[builtins.str, typing.Any]],
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    certificate_arn: typing.Optional[builtins.str] = None,
    create_usage_plan: typing.Optional[builtins.bool] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    custom_routes: typing.Optional[typing.Sequence[typing.Union[CustomRoute, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b97171af667de8a26858df1339c97d506d81da9dd597dd76896abec03c25e8f4(
    *,
    api_name: builtins.str,
    lambda_api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.LambdaRestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
    proxy: typing.Optional[builtins.bool] = None,
    rest_api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.RestApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0ea30b15daf73de785b4991457443ee0ca220224fbd08155a17d86c67413930(
    *,
    max_capacity: jsii.Number,
    min_capacity: jsii.Number,
    cpu_scale: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.CpuUtilizationScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
    memory_scale: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.MemoryUtilizationScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54ea2679bab87dfe8eb538ebc455f8d93200c1beb37ad6e093fa52678f8ac1fc(
    *,
    container_port: jsii.Number,
    image: _aws_cdk_aws_ecs_ceddda9d.ContainerImage,
    health_check: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.HealthCheck, typing.Dict[builtins.str, typing.Any]]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__037506344a4229895450ab2466c4a39abd0da2085c3a5d744bc1a0bdaf3a2c8d(
    *,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    method: builtins.str,
    path: builtins.str,
    method_options: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.MethodOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19ac4f77d3bba1391929b87d2d23b70fe61e21aa6809f43ed4283d6ecf350909(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    containers: typing.Sequence[typing.Union[ContainerProps, typing.Dict[builtins.str, typing.Any]]],
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    service_name: builtins.str,
    subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    alb_target_port: typing.Optional[jsii.Number] = None,
    auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_public_load_balancer: typing.Optional[builtins.bool] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    task_cpu: typing.Optional[jsii.Number] = None,
    task_exec_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    task_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e1edfc306738ea99e0bd03a55876d7f75a063970dd3103fc1bbb766dff014b1(
    *,
    certificates: typing.Sequence[_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate],
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    containers: typing.Sequence[typing.Union[ContainerProps, typing.Dict[builtins.str, typing.Any]]],
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    service_name: builtins.str,
    subnets: typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]],
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    alb_target_port: typing.Optional[jsii.Number] = None,
    auto_scaling: typing.Optional[typing.Union[AutoScalingProps, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_public_load_balancer: typing.Optional[builtins.bool] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    task_cpu: typing.Optional[jsii.Number] = None,
    task_exec_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    task_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c063f743e1f72b467dbd5e3c1b50e12ced31a4dc57d989ab67b5420ebfa12ce(
    connect_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    disconnect_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    default_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__086f4831c9bd7268c4a6f1ebbd644aefacbb7ff7cc1b52e6393dcd78ac290b95(
    route_key: builtins.str,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    route_response_selection_expression: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18bbe2305cfca74cc21cbc3685c858f68a283a4e8175a04cb1f1cfceee1d48e2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    domain_name: typing.Optional[builtins.str] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ef8aa08462eac4d715eed8d4ba1eebf11c6b448eaa5babff0820753e58341bf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    default_handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    routes: typing.Sequence[typing.Union[WebSocketRoute, typing.Dict[builtins.str, typing.Any]]],
    domain_name: typing.Optional[builtins.str] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15689bf8cb45b613fd6d0271ea2d2b2a40c677ff7ee1d37b34596aa645c185e9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    web_socket_api: typing.Union[WebSocketApiProps, typing.Dict[builtins.str, typing.Any]],
    certificate_arn: typing.Optional[builtins.str] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    custom_routes: typing.Optional[typing.Sequence[typing.Union[WebSocketRoute, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63f4cdf57fbe667cd56ca0962570b3a041ac0113f05528d7f2964cb201e11e6e(
    *,
    lambda_function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    web_socket_api: typing.Union[WebSocketApiProps, typing.Dict[builtins.str, typing.Any]],
    certificate_arn: typing.Optional[builtins.str] = None,
    custom_domain_name: typing.Optional[builtins.str] = None,
    custom_routes: typing.Optional[typing.Sequence[typing.Union[WebSocketRoute, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    hosted_zone: typing.Optional[_aws_cdk_aws_route53_ceddda9d.IHostedZone] = None,
    log_group_props: typing.Optional[typing.Union[_aws_cdk_aws_logs_ceddda9d.LogGroupProps, typing.Dict[builtins.str, typing.Any]]] = None,
    stage_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2283390d86917e3d80fc2b4212dba64f234ec0bfdb8a83f8fc6c17d748dc71cc(
    *,
    api_name: builtins.str,
    api_props: typing.Optional[typing.Union[_aws_cdk_aws_apigatewayv2_ceddda9d.WebSocketApiProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34bf0c8251244f50bde7c9d5fe60d88348a1be2cec9ac52b2fae8d7918d72b62(
    *,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    route_key: builtins.str,
    route_response_selection_expression: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
