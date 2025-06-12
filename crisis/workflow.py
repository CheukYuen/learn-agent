from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Callable
from util import llm_call, extract_xml

def chain(input: str, prompts: List[str]) -> str:
    """Chain multiple LLM calls sequentially, passing results between steps."""
    result = input
    for i, prompt in enumerate(prompts, 1):
        print(f"\nStep {i}:")
        result = llm_call(f"{prompt}\nInput: {result}")
        print(result)
    return result

def parallel(prompt: str, inputs: List[str], n_workers: int = 3) -> List[str]:
    """Process multiple inputs concurrently with the same prompt."""
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(llm_call, f"{prompt}\nInput: {x}") for x in inputs]
        return [f.result() for f in futures]

def route(input: str, routes: Dict[str, str]) -> str:
    """Route input to specialized prompt using content classification."""
    # First determine appropriate route using LLM with chain-of-thought
    print(f"\nAvailable routes: {list(routes.keys())}")
    selector_prompt = f"""
    Analyze the input and select the most appropriate support team from these options: {list(routes.keys())}
    First explain your reasoning, then provide your selection in this XML format:

    <reasoning>
    Brief explanation of why this ticket should be routed to a specific team.
    Consider key terms, user intent, and urgency level.
    </reasoning>

    <selection>
    The chosen team name
    </selection>

    Input: {input}""".strip()
    
    route_response = llm_call(selector_prompt)
    reasoning = extract_xml(route_response, 'reasoning')
    route_key = extract_xml(route_response, 'selection').strip().lower()
    
    print("Routing Analysis:")
    print(reasoning)
    print(f"\nSelected route: {route_key}")
    
    # Process input with selected specialized prompt
    selected_prompt = routes[route_key]
    return llm_call(f"{selected_prompt}\nInput: {input}")

def analyze_alert(alert_details: str) -> str:
    """
    Analyze alert by first classifying it, then applying appropriate specialized analysis.
    
    Args:
        alert_details: The alert information to analyze
        
    Returns:
        Comprehensive analysis based on alert category
    """
    
    # Step 1: Load classification prompt
    with open('crisis/alert-classification-prompt.md', 'r', encoding='utf-8') as f:
        classification_prompt = f.read().replace('{{ALERT_DETAILS}}', alert_details)
    
    # Step 2: Classify the alert
    print("\n=== 告警分类阶段 ===")
    classification_response = llm_call(classification_prompt)
    
    # Extract classification results
    category = extract_xml(classification_response, 'category').strip().lower()
    reasoning = extract_xml(classification_response, 'reasoning')
    confidence = extract_xml(classification_response, 'confidence')
    
    print(f"分类结果: {category}")
    print(f"分类依据: {reasoning}")
    print(f"置信度: {confidence}")
    
    # Step 3: Apply specialized analysis based on category
    print(f"\n=== {category.upper()} 专项分析阶段 ===")
    
    if category == 'uni_error':
        # For Uni errors, just return error code explanation
        with open('crisis/uni-error-prompt.md', 'r', encoding='utf-8') as f:
            prompt = f.read().replace('{{ALERT_DETAILS}}', alert_details)
        analysis_result = llm_call(prompt)
        
    elif category == 'javascript_error':
        # For JavaScript errors, analyze and prepare for code scanning
        with open('crisis/javascript-error-prompt.md', 'r', encoding='utf-8') as f:
            prompt = f.read().replace('{{ALERT_DETAILS}}', alert_details)
        analysis_result = llm_call(prompt)
        
        # TODO: Implement code repository scanning
        print("\n[待实现] 代码库扫描功能...")
        
    elif category == 'backend_api_error':
        # For backend API errors, analyze and prepare for code scanning
        with open('crisis/backend-api-error-prompt.md', 'r', encoding='utf-8') as f:
            prompt = f.read().replace('{{ALERT_DETAILS}}', alert_details)
        analysis_result = llm_call(prompt)
        
        # TODO: Implement code repository scanning
        print("\n[待实现] 代码库扫描功能...")
        
    else:
        # Fallback to general analysis for unknown categories
        print(f"未知类别 {category}，使用通用分析...")
        with open('crisis/analysis-prompt.md', 'r', encoding='utf-8') as f:
            prompt = f.read().replace('{{ALERT_DETAILS}}', alert_details)
        analysis_result = llm_call(prompt)
    
    # Combine classification and analysis results
    final_result = f"""
=== 告警分类结果 ===
类别: {category}
置信度: {confidence}
分类依据: {reasoning}

=== 专项分析结果 ===
{analysis_result}
"""
    
    return final_result