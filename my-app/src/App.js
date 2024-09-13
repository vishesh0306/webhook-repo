import React, { useState, useEffect } from 'react';

function App() {
  const [events, setEvents] = useState([]);

  // Fetch data every 15 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('https://4b9c-43-225-72-169.ngrok-free.app/events');
        const data = await response.json();
        setEvents(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();  // Fetch once when component mounts
    const interval = setInterval(fetchData, 15000);  // Poll every 15 seconds

    return () => clearInterval(interval);  // Cleanup interval when component unmounts
  }, []);

  return (
    <div className="App">
      <h1>GitHub Repository Events</h1>
      <ul>
        {events.map((event, index) => (
          <li key={index}>
            {event.author} {getActionText(event)}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Function to format the event details
function getActionText(event) {
  const timestamp = new Date(event.timestamp).toUTCString();
  if (event.actionType === 'PUSH') {
    return `pushed to ${event.toBranch} on ${timestamp}`;
  } else if (event.actionType === 'PULL_REQUEST') {
    return `submitted a pull request from ${event.fromBranch} to ${event.toBranch} on ${timestamp}`;
  } else if (event.actionType === 'MERGE') {
    return `merged branch ${event.fromBranch} to ${event.toBranch} on ${timestamp}`;
  }
  return '';
}

export default App;
