from django.test import TransactionTestCase
from srcs_user.tests.factories import UserFactory
from srcs_game import services as gameServices

class GameTests(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        self.left_player = UserFactory()
        self.right_player = UserFactory()

    def tearDown(self):
        UserFactory.reset_sequence()

    def test_player_invitation_for_a_game(self):
        """ On invitation a message need to be created with an option to accept or reject the match """
        pass

    def test_valid_game_creation(self):
        """ Check the creation of a blank game with 2 players that exists """
        pass

    def test_invalid_game_creation_should_fail(self):
        """ Test the exception raise on an invalid game creation """
        pass

    def test_compute_game_score(self):
        """ Set the score at the end of the game (? and the winner ?) """
        pass

    def test_game_end_due_to_lagging(self):
        """ When at least one of the players is experimenting a poor connection, the game should stop and no points computed """
        pass

    def test_game_end_due_to_disconnection(self):
        """ When at least one of the players is disconnected, the game should stop but the mmr points should change """
        pass
    
    def test_find_blind_match_should_create_a_game_with_the_closest_mmr_player_looking_for_a_game(self):
        """ When more than 2 players are waiting for a blind match,
        the matchmaking system should create a game with players with closest mmr value """
        pass

    def test_find_blind_match_should_wait_for_a_more_compatible_pair_before_unfair_game_creation(self):
        """ When only two players with large difference of mmr are looking for a blind match,
        the matchmaking system should wait for a while before create a match with then """
        pass
    