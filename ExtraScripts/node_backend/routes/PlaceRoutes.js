// Import required modules
const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');
const router = express.Router();

// MongoDB connection details
const uri = "mongodb+srv://dlovej009:Dheeraj2006@cluster0.dnu8vna.mongodb.net/?retryWrites=true&w=majority";
const client = new MongoClient(uri);
let placeCollection;

// Connect to MongoDB
client.connect()
    .then(() => {
        const db = client.db("ScouterPlaces");
        placeCollection = db.collection("Places");
        console.log("Database connected");
    })
    .catch((error) => {
        console.error("Database connection failed:", error);
    });

// Route to fetch all places
router.get('/places', async (req, res) => {
    try {
        // Fetch only the specified fields using projection
        const places = await placeCollection
            .find({}, { projection: { currentPopularity: 1, Longitude: 1, Latitude: 1, PlaceName: 1, placeID: 1, GooglePlaceName: 1 } })
            .toArray();

        res.status(200).json({
            success: true,
            data: places,
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: "Failed to fetch places",
            error: error.message,
        });
    }
});
// Route to create a new place
router.post('/places', async (req, res) => {
    try {
        const newPlace = req.body;
        const result = await placeCollection.insertOne(newPlace);
        res.status(201).json({
            success: true,
            message: "Place created successfully",
            data: result.ops[0],
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: "Failed to create place",
            error: error.message,
        });
    }
});

// Route to update a place (currentPopularity only)
router.put('/places/:id', async (req, res) => {
    console.log("db")
    console.log(req.body)
    try {
       
        const { id } = req.params;
        const { currentPopularity } = req.body;

        if (!currentPopularity) {
            return res.status(400).json({
                success: false,
                message: "Missing currentPopularity in request body",
            });
        }

        const result = await placeCollection.updateOne(
            { _id: id },
            { $set: { currentPopularity } }
        );

        if (result.matchedCount === 0) {
            return res.status(404).json({
                success: false,
                message: "Place not found",
            });
        }

        res.status(200).json({
            success: true,
            message: "Place updated successfully",
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: "Failed to update place",
            error: error.message,
        });
    }
});

// Route to delete a place
router.delete('/places/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const result = await placeCollection.deleteOne({ _id: new ObjectId(id) });

        if (result.deletedCount === 0) {
            return res.status(404).json({
                success: false,
                message: "Place not found",
            });
        }

        res.status(200).json({
            success: true,
            message: "Place deleted successfully",
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: "Failed to delete place",
            error: error.message,
        });
    }
});

module.exports = router;

