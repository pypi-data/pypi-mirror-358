"""
AgentMeter Decorators for automatic usage tracking
"""

import functools
import time
from typing import Optional, Dict, Any, Callable, Union
from .client import AgentMeterClient
from .models import PaymentType


def meter_api_request_pay(
    client: AgentMeterClient,
    unit_price: float = 0.001,
    project_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    user_id_param: str = "user_id",
    api_calls: int = 1
):
    """
    Decorator for tracking API request payments
    
    Args:
        client: AgentMeter client instance
        unit_price: Price per API request (default: $0.001)
        project_id: Project ID (optional, uses client default)
        agent_id: Agent ID (optional, uses client default)
        user_id_param: Parameter name containing user_id (default: "user_id")
        api_calls: Number of API calls per function execution (default: 1)
    
    Example:
        @meter_api_request_pay(client, unit_price=0.3)
        def search_products(query: str, user_id: str):
            return perform_search(query)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            metadata = {}
            
            # Extract metadata using provided function
            if user_id_param in kwargs:
                metadata[user_id_param] = kwargs[user_id_param]
            
            # Add timing and function metadata
            metadata.update({
                "function_name": func.__name__,
                "module": func.__module__,
                "start_time": start_time
            })
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Add execution metadata
                end_time = time.time()
                metadata.update({
                    "duration_seconds": end_time - start_time,
                    "end_time": end_time,
                    "status": "success"
                })
                
                # Record the payment event
                client.record_api_request_pay(
                    api_calls=api_calls,
                    unit_price=unit_price,
                    project_id=project_id,
                    agent_id=agent_id,
                    user_id=kwargs.get(user_id_param),
                    metadata=metadata
                )
                
                return result
                
            except Exception as e:
                # Record failed execution
                end_time = time.time()
                metadata.update({
                    "duration_seconds": end_time - start_time,
                    "end_time": end_time,
                    "status": "error",
                    "error": str(e)
                })
                
                # Still record the event (failed API calls should also be metered)
                try:
                    client.record_api_request_pay(
                        api_calls=api_calls,
                        unit_price=unit_price,
                        project_id=project_id,
                        agent_id=agent_id,
                        user_id=kwargs.get(user_id_param),
                        metadata=metadata
                    )
                except:
                    pass  # Don't fail the original function if metering fails
                
                raise  # Re-raise the original exception
        
        return wrapper
    return decorator


def meter_token_based_pay(
    client: AgentMeterClient,
    input_token_price: float = 0.000004,
    output_token_price: float = 0.000001,
    project_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    user_id_param: str = "user_id",
    extract_tokens: bool = True
):
    """
    Decorator for tracking token-based payments
    
    Args:
        client: AgentMeter client instance
        input_token_price: Price per input token (default: $0.000004)
        output_token_price: Price per output token (default: $0.000001)
        project_id: Project ID (optional, uses client default)
        agent_id: Agent ID (optional, uses client default)
        user_id_param: Parameter name containing user_id (default: "user_id")
        extract_tokens: Whether to automatically extract token counts (default: True)
    
    Example:
        @meter_token_based_pay(client)
        def generate_content(prompt: str, user_id: str):
            response = llm.generate(prompt)
            return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            metadata = {}
            tokens_in, tokens_out = 0, 0
            
            # Extract metadata using provided function
            if user_id_param in kwargs:
                metadata[user_id_param] = kwargs[user_id_param]
            
            # Add timing and function metadata
            metadata.update({
                "function_name": func.__name__,
                "module": func.__module__,
                "start_time": start_time
            })
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Extract token counts
                if extract_tokens:
                    try:
                        tokens_in, tokens_out = extract_tokens(*args, result=result, **kwargs)
                    except Exception as e:
                        metadata["token_extraction_error"] = str(e)
                
                # Add execution metadata
                end_time = time.time()
                metadata.update({
                    "duration_seconds": end_time - start_time,
                    "end_time": end_time,
                    "status": "success",
                    "extracted_tokens_in": tokens_in,
                    "extracted_tokens_out": tokens_out
                })
                
                # Record the payment event
                client.record_token_based_pay(
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    input_token_price=input_token_price,
                    output_token_price=output_token_price,
                    project_id=project_id,
                    agent_id=agent_id,
                    user_id=kwargs.get(user_id_param),
                    metadata=metadata
                )
                
                return result
                
            except Exception as e:
                # Record failed execution
                end_time = time.time()
                metadata.update({
                    "duration_seconds": end_time - start_time,
                    "end_time": end_time,
                    "status": "error",
                    "error": str(e)
                })
                
                # Still record the event with any tokens we managed to extract
                try:
                    client.record_token_based_pay(
                        tokens_in=tokens_in,
                        tokens_out=tokens_out,
                        input_token_price=input_token_price,
                        output_token_price=output_token_price,
                        project_id=project_id,
                        agent_id=agent_id,
                        user_id=kwargs.get(user_id_param),
                        metadata=metadata
                    )
                except:
                    pass  # Don't fail the original function if metering fails
                
                raise  # Re-raise the original exception
        
        return wrapper
    return decorator


def meter_instant_pay(
    client: AgentMeterClient,
    amount: float,
    description: str = "Premium feature",
    project_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    user_id_param: str = "user_id",
    condition: Optional[Callable] = None
):
    """
    Decorator for tracking instant payments
    
    Args:
        client: AgentMeter client instance
        amount: Fixed amount to charge
        description: Payment description (default: "Premium feature")
        project_id: Project ID (optional, uses client default)
        agent_id: Agent ID (optional, uses client default)
        user_id_param: Parameter name containing user_id (default: "user_id")
        condition: Optional function to determine if payment should be charged
    
    Example:
        @meter_instant_pay(client, amount=4.99, description="Advanced search")
        def advanced_search(query: str, user_id: str):
            return perform_advanced_search(query)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            metadata = {}
            should_charge = True
            
            # Check condition if provided
            if condition:
                try:
                    should_charge = condition(*args, **kwargs)
                except Exception as e:
                    metadata["condition_error"] = str(e)
                    should_charge = True  # Default to charging if condition check fails
            
            # Extract metadata using provided function
            if user_id_param in kwargs:
                metadata[user_id_param] = kwargs[user_id_param]
            
            # Add timing and function metadata
            metadata.update({
                "function_name": func.__name__,
                "module": func.__module__,
                "start_time": start_time,
                "should_charge": should_charge
            })
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Add execution metadata
                end_time = time.time()
                metadata.update({
                    "duration_seconds": end_time - start_time,
                    "end_time": end_time,
                    "status": "success"
                })
                
                # Record the payment event only if conditions are met
                if should_charge:
                    client.record_instant_pay(
                        amount=amount,
                        description=description,
                        project_id=project_id,
                        agent_id=agent_id,
                        user_id=kwargs.get(user_id_param),
                        metadata=metadata
                    )
                
                return result
                
            except Exception as e:
                # Record failed execution
                end_time = time.time()
                metadata.update({
                    "duration_seconds": end_time - start_time,
                    "end_time": end_time,
                    "status": "error",
                    "error": str(e)
                })
                
                # Don't charge for failed executions unless specifically configured to do so
                # This can be customized based on business logic
                
                raise  # Re-raise the original exception
        
        return wrapper
    return decorator


def meter_function(
    client: AgentMeterClient,
    payment_type: PaymentType = PaymentType.API_REQUEST_PAY,
    **payment_kwargs
):
    """
    Generic decorator that can handle different payment types
    
    Args:
        client: AgentMeter client instance
        payment_type: Type of payment to track
        **payment_kwargs: Payment-specific arguments
    
    Example:
        @meter_function(client, PaymentType.API_REQUEST_PAY, unit_price=0.3)
        def api_call():
            pass
        
        @meter_function(client, PaymentType.INSTANT_PAY, amount=4.99)
        def premium_feature():
            pass
    """
    if payment_type == PaymentType.API_REQUEST_PAY:
        return meter_api_request_pay(client, **payment_kwargs)
    elif payment_type == PaymentType.TOKEN_BASED_PAY:
        return meter_token_based_pay(client, **payment_kwargs)
    elif payment_type == PaymentType.INSTANT_PAY:
        return meter_instant_pay(client, **payment_kwargs)
    else:
        raise ValueError(f"Unsupported payment type: {payment_type}")


def meter_agent(
    client: AgentMeterClient,
    payment_type: PaymentType = PaymentType.API_REQUEST_PAY,
    methods_to_meter: Optional[list] = None,
    **payment_kwargs
):
    """
    Class decorator for automatically metering agent methods
    
    Args:
        client: AgentMeter client instance
        payment_type: Type of payment to track
        methods_to_meter: List of method names to meter (if None, meters all public methods)
        **payment_kwargs: Payment-specific arguments
    
    Example:
        @meter_agent(client, PaymentType.API_REQUEST_PAY, unit_price=0.1)
        class SearchAgent:
            def search(self, query):
                return perform_search(query)
            
            def _internal_method(self):  # Won't be metered (private method)
                pass
    """
    def decorator(cls):
        # Get methods to meter
        if methods_to_meter is None:
            # Meter all public methods (not starting with _)
            methods_to_meter_list = [
                name for name in dir(cls) 
                if not name.startswith('_') and callable(getattr(cls, name))
            ]
        else:
            methods_to_meter_list = methods_to_meter
        
        # Apply metering decorator to each method
        for method_name in methods_to_meter_list:
            if hasattr(cls, method_name):
                original_method = getattr(cls, method_name)
                if callable(original_method):
                    metered_method = meter_function(
                        client, payment_type, **payment_kwargs
                    )(original_method)
                    setattr(cls, method_name, metered_method)
        
        return cls
    return decorator