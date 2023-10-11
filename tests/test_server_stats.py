import pytest
from unittest.mock import Mock, patch
from analysis.server_stats import handle_serverstats


@pytest.mark.asyncio
async def test_handle_serverstats():
    # Mocking the message and its associated methods/attributes
    mock_message = Mock()
    mock_message.guild.name = "TestServer"
    mock_message.channel.send = Mock()

    # Mocking database and other external function calls
    with patch('database.db.get_top_users', return_value=[("user1", 50), ("user2", 30)]), \
            patch('database.db.get_top_mentioners', return_value=[]), \
            patch('database.db.get_active_channels', return_value=[]), \
            patch('database.db.get_total_messages', return_value=150), \
            patch("analysis.server_stats.get_total_links_shared", return_value=20), \
         patch("analysis.server_stats.get_message_with_mentions_count", return_value=10), \
         patch("analysis.server_stats.get_most_mentioned_users", return_value=[("user3", 3)]), \
         patch("analysis.server_stats.get_busiest_hour", return_value=("Monday", 10)), \
         patch("analysis.server_stats.get_busiest_day", return_value=("Monday", 50)), \
         patch("analysis.server_stats.get_unique_users", return_value=10), \
         patch("analysis.server_stats.get_avg_messages_per_user", return_value=5.0), \
         patch("analysis.server_stats.get_user_growth_over_time", return_value=[("2023-10-10", 5)]), \
         patch("analysis.server_stats.plot_user_growth", return_value="path/to/image.png"):

        await handle_serverstats(mock_message)

        # 1. Ensure the function sends a message
        mock_message.channel.send.assert_called()

        # 2. Validate the content of the message
        args, _ = mock_message.channel.send.call_args
        assert ":bar_chart: **Server Statistics for TestServer**" in args[0]
        assert ":envelope: **Total Messages**: 150" in args[0]
        assert ":link: **Total Links Shared**: 20" in args[0]
        assert ":loudspeaker: **Messages with Mentions**: 10" in args[0]
        assert "⏰ **Busiest Time of Day**: 10:00 - 11:00 on Monday" in args[0]
        assert "📅 **Busiest Day of the Week**: Monday" in args[0]
        assert "👥 **Number of Unique Users**: 10" in args[0]
        assert "📩 **Average Messages per User**: 5.00" in args[0]
        assert ":trophy: **Top 3 Active Users**:" in args[0]
        assert ":bust_in_silhouette: user1 - 50 messages" in args[0]
        assert ":star2: **Top 3 Mentioners**:" in args[0]
        assert ":loud_sound: **Top 3 Active Channels**:" in args[0]
        assert "🏆 **Top 3 Most Mentioned Users**:" in args[0]
        assert "📣 user3 - 3 mentions" in args[0]

        # 3. Ensure the function sends the image
        args, kwargs = mock_message.channel.send.call_args_list[1]
        assert kwargs['file'].filename == "images/user_growth.png"

        # 4. Number of times the send method is called
        assert mock_message.channel.send.call_count == 2
        