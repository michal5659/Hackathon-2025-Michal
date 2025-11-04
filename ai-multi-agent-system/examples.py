"""
Sample usage examples for the AI Multi-Agent Orchestration System
"""
import asyncio
from orchestrator import get_orchestrator
from services import get_message_pull_service
from agents import get_classification_agent


async def example_1_process_single_message():
    """Example 1: Process a single message"""
    print("=== Example 1: Process Single Message ===")
    
    orchestrator = get_orchestrator()
    
    # Sample message
    message = {
        'message_id': 'test-001',
        'channel': 'email',
        'sender': 'customer@example.com',
        'content': 'I would like to check the status of my claim #CLM-12345',
        'timestamp': '2025-11-03T10:00:00',
        'metadata': {'subject': 'Claim Status Inquiry'}
    }
    
    result = await orchestrator.process_message(message)
    print(f"Result: {result}")


async def example_2_classify_only():
    """Example 2: Just classify a message without executing"""
    print("\n=== Example 2: Classification Only ===")
    
    classifier = get_classification_agent()
    
    message = {
        'message_id': 'test-002',
        'channel': 'whatsapp',
        'sender': '+1234567890',
        'content': 'I need to submit a new insurance claim for my car accident',
        'timestamp': '2025-11-03T11:00:00',
        'metadata': {}
    }
    
    classification = classifier.classify_message(message)
    print(f"Classification: {classification}")


async def example_3_process_batch():
    """Example 3: Process multiple messages"""
    print("\n=== Example 3: Batch Processing ===")
    
    orchestrator = get_orchestrator()
    
    messages = [
        {
            'message_id': 'test-003',
            'channel': 'email',
            'sender': 'user1@example.com',
            'content': 'What are my policy details?',
            'timestamp': '2025-11-03T12:00:00',
            'metadata': {}
        },
        {
            'message_id': 'test-004',
            'channel': 'teams',
            'sender': 'user2',
            'content': 'I want to update my contact information',
            'timestamp': '2025-11-03T12:05:00',
            'metadata': {}
        },
        {
            'message_id': 'test-005',
            'channel': 'whatsapp',
            'sender': '+9876543210',
            'content': 'When is my next payment due?',
            'timestamp': '2025-11-03T12:10:00',
            'metadata': {}
        }
    ]
    
    results = await orchestrator.process_messages(messages)
    print(f"Processed {len(results)} messages")
    for result in results:
        print(f"  - {result['message_id']}: {result['status']}")


async def example_4_send_response():
    """Example 4: Send a response to a specific channel"""
    print("\n=== Example 4: Send Response ===")
    
    message_service = get_message_pull_service()
    
    # Send email response
    success = await message_service.send_response(
        channel='email',
        recipient='customer@example.com',
        content='Your policy inquiry has been received and is being processed.',
        metadata={'subject': 'Re: Policy Inquiry'}
    )
    
    print(f"Email sent: {success}")


async def example_5_pull_messages():
    """Example 5: Pull messages from all channels"""
    print("\n=== Example 5: Pull Messages ===")
    
    message_service = get_message_pull_service()
    
    # Pull from all channels
    messages = await message_service.pull_all_messages()
    print(f"Pulled {len(messages)} messages from all channels")
    
    # Pull from specific channel
    email_messages = await message_service.pull_from_channel('email')
    print(f"Pulled {len(email_messages)} messages from email")


async def run_all_examples():
    """Run all examples"""
    print("AI Multi-Agent Orchestration System - Usage Examples\n")
    
    try:
        await example_1_process_single_message()
        await example_2_classify_only()
        await example_3_process_batch()
        await example_4_send_response()
        await example_5_pull_messages()
        
        print("\n=== All Examples Completed ===")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")


if __name__ == "__main__":
    # Make sure you have your .env file configured before running
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(run_all_examples())
