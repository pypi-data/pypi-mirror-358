from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def test_football_prediction_market():
    # Deploy Contract
    factory = get_contract_factory("PredictionMarket")
    contract = factory.deploy(args=["2024-06-26", "Georgia", "Portugal"])

    # Resolve match
    transaction_response_call_1 = contract.resolve(args=[])
    assert tx_execution_succeeded(transaction_response_call_1)

    # Get Updated State
    contract_state_2 = contract.get_resolution_data(args=[])

    assert contract_state_2["winner"] == 1
    assert contract_state_2["score"] == "2:0"
    assert contract_state_2["has_resolved"] == True
