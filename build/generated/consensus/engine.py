import time

class DistributedConsensusEngine:
    def __init__(self, node_id):
        self.node_id = node_id
        self.current_term = 0
        self.state = "follower"
        self.votes_received = set()

    def start_election(self):
        self.current_term += 1
        self.state = "candidate"
        self.votes_received = {self.node_id}
        print(f"[CONSENSUS-ENGINE] Node {self.node_id} initiated election term {self.current_term}")

    def cast_vote(self, candidate_id, term):
        if term > self.current_term:
            self.current_term = term
            self.state = "follower"
            print(f"[CONSENSUS-ENGINE] Node {self.node_id} voted for candidate {candidate_id} in term {term}")
            return True
        return False