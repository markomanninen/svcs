// Before: Uses external dependencies
import express from 'express';
import lodash from 'lodash';
import mongoose from 'mongoose';

const app = express();

app.use(express.json());

const userSchema = new mongoose.Schema({
    name: String,
    email: String
});

function processUsers(users) {
    return lodash.uniqBy(users, 'email');
}
