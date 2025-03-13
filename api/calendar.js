// In-memory storage for calendar events (in a real app, this would be a database)
const events = [];

module.exports = (req, res) => {
  if (req.method === 'GET') {
    // Return all events
    res.status(200).json(events);
  } else if (req.method === 'POST') {
    // Create a new event
    const { title, start_time } = req.body;
    
    if (!title || !start_time) {
      return res.status(400).json({ error: 'Missing required fields. Required: title, start_time' });
    }
    
    const event = {
      id: String(events.length + 1),
      title,
      start_time
    };
    
    events.push(event);
    res.status(201).json(event);
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
} 