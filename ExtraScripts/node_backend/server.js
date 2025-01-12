const express = require('express');
const placesRoute = require('./routes/PlaceRoutes');
const cors = require('cors');

const app = express();

// Enable CORS for all routes and all origins
app.use(cors());

const port = process.env.PORT || 9090;

app.use(express.json());
app.use('/api', placesRoute);

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
