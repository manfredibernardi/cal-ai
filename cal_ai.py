#!/usr/bin/env python3
"""
NutriVision - Meal Analysis App

This script serves as the entry point for the NutriVision application,
which analyzes food images to provide calorie estimates and macronutrient breakdowns.

Usage:
    python cal_ai.py
"""

from app import app

if __name__ == "__main__":
    print("Starting NutriVision - Meal Analysis App")
    print("Open your browser and navigate to: http://127.0.0.1:5000/")
    app.run(debug=True, host='0.0.0.0')
