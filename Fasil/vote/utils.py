from django.db import transaction
from .models import VotingToken
import uuid
from django.conf import settings

def create_voting_tokens(amount, father, debate, price, entity='paid', invited_by=None):
    """
    Create a specified amount of VotingToken objects for a given father.

    Args:
        amount (int): The number of tokens to create.
        father (CustomUser): The CustomUser object associated with the tokens.
        price (int): The price of token to create.
        entity (str): The entity type for the tokens ('paid' or 'invited').
        invited_by (Sponsor): The sponsor associated with the tokens if entity is 'invited'.

    Returns:
        list: List of created VotingToken objects.
    """
    with transaction.atomic():
        tokens = []
        for _ in range(amount):
            if price == None:
                price = settings.DEFAULT_TOKEN_PRICE
            token = VotingToken.objects.create(
                hash=generate_unique_hash(),  # Replace with your hash generation logic
                father=father,
                debate = debate,
                price=price,  # Replace with the desired default price
                used=False,
                entity=entity,
                invited_by=invited_by if entity == 'invited' else None,
            )
            tokens.append(token)
        return tokens

def generate_unique_hash():
    """
    Generate a unique hash for VotingToken using UUID.

    Returns:
        str: Unique hash string.
    """
    unique_hash = str(uuid.uuid4())  # Generate a random UUID
    return unique_hash

def transfer_token(token, sender, reciever):
    """
    Transfer a VotingToken object for a given receiver.

    Args:
        token (VotingToken): The VotingToken object that should be transfered.
        sender (CustomUser): The CustomUser object associated with the token.
        receiver (CustomUser): The CustomUser object to receieve the token.

    Returns:
        bool: Respond with True | False of the transfer process.
    """
    return None
