from dataclasses import dataclass


@dataclass
class InfiniGramEngineException(Exception):
    detail: str
