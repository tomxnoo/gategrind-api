# **GateGrind V2 - Project Overview**

Version: 2.1 (Definitive)  
Date: 2025-07-24  
Author: John, BMad Product Manager

## **1. Introduction & Project Vision**

### **1.1. Project Overview**

This document outlines the Product Requirements for the **GateGrind V2** backend. This project is a hybrid, best described as **"Brownfield x Greenfield = V2"**.

* **Greenfield**: We will build the new V2 game systems (Awakening, Dungeons, Aura, Skill Tree) from the ground up on a clean, modern architecture.  
* **Brownfield**: We will re-implement the best, proven features from the existing V1 system (Movement Logging, XP Engine, Incursions) into the new V2 architecture, ensuring their logic is preserved and enhanced.

The primary goal is to create a single, authoritative API that serves as the "source of truth" for all game mechanics. This API will integrate seamlessly with the existing, high-quality Python Discord bot UI and future applications like webapp and mobile app.

### **1.2. Core Product Goals**

* **Build a True RPG Fitness Experience**: Create an engaging game with deep progression, strategic choices, and rewarding gameplay loops.  
* **Preserve the "Living Nexus" UI**: The backend must fully support and enhance the existing ephemeral, panel-based Discord UI.  
* **Establish a Scalable Foundation**: Create a clean, modular, and well-tested codebase for future growth.  
* **Unify Progression**: Implement the "Aura" system as a single, compelling metric of a user's total power.