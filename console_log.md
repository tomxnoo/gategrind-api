~/workspace$ python fix.py
🚀 Starting Fixed Movement Redistribution Script
============================================================
✅ Connected to database successfully

📊 Starting movement redistribution...

🏗️  Ensuring skill tree nodes exist...
Found 39 movement categories
  Processing category: Balance (ID: BALANCE)
    ✓ Node exists: balance_1
    ✓ Node exists: balance_2
    ✓ Node exists: balance_3
    ✓ Node exists: balance_4
    ✓ Node exists: balance_5
  Processing category: Bridge Skills (ID: BRIDGE)
    ❌ Failed to create node bridge_skills_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (438, 2025-07-29 18:11:17.814441+00, 2025-07-29 18:11:17.814441+00, bridge_skills_1, BRIDGE, 1, Bridge Skills Level 1, Level 1 progression for Bridge Skills, null, null, 1, 100, 50, 75).
    ❌ Failed to create node bridge_skills_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (439, 2025-07-29 18:11:18.127413+00, 2025-07-29 18:11:18.127413+00, bridge_skills_2, BRIDGE, 2, Bridge Skills Level 2, Level 2 progression for Bridge Skills, null, null, 2, 200, 100, 150).
    ❌ Failed to create node bridge_skills_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (440, 2025-07-29 18:11:18.336702+00, 2025-07-29 18:11:18.336702+00, bridge_skills_3, BRIDGE, 3, Bridge Skills Level 3, Level 3 progression for Bridge Skills, null, null, 3, 300, 150, 225).
    ❌ Failed to create node bridge_skills_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (441, 2025-07-29 18:11:18.544595+00, 2025-07-29 18:11:18.544595+00, bridge_skills_4, BRIDGE, 4, Bridge Skills Level 4, Level 4 progression for Bridge Skills, null, null, 4, 400, 200, 300).
    ❌ Failed to create node bridge_skills_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (442, 2025-07-29 18:11:18.752183+00, 2025-07-29 18:11:18.752183+00, bridge_skills_5, BRIDGE, 5, Bridge Skills Level 5, Level 5 progression for Bridge Skills, null, null, 5, 500, 250, 375).
  Processing category: Cardio (ID: CARDIO)
    ✓ Node exists: cardio_1
    ✓ Node exists: cardio_2
    ✓ Node exists: cardio_3
    ✓ Node exists: cardio_4
    ✓ Node exists: cardio_5
  Processing category: Interval Training (ID: CARDIO_INTERVAL)
    ❌ Failed to create node interval_training_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (443, 2025-07-29 18:11:19.479416+00, 2025-07-29 18:11:19.479416+00, interval_training_1, CARDIO_INTERVAL, 1, Interval Training Level 1, Level 1 progression for Interval Training, null, null, 1, 100, 50, 75).
    ❌ Failed to create node interval_training_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (444, 2025-07-29 18:11:19.688223+00, 2025-07-29 18:11:19.688223+00, interval_training_2, CARDIO_INTERVAL, 2, Interval Training Level 2, Level 2 progression for Interval Training, null, null, 2, 200, 100, 150).
    ❌ Failed to create node interval_training_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (445, 2025-07-29 18:11:19.89571+00, 2025-07-29 18:11:19.89571+00, interval_training_3, CARDIO_INTERVAL, 3, Interval Training Level 3, Level 3 progression for Interval Training, null, null, 3, 300, 150, 225).
    ❌ Failed to create node interval_training_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (446, 2025-07-29 18:11:20.10363+00, 2025-07-29 18:11:20.10363+00, interval_training_4, CARDIO_INTERVAL, 4, Interval Training Level 4, Level 4 progression for Interval Training, null, null, 4, 400, 200, 300).
    ❌ Failed to create node interval_training_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (447, 2025-07-29 18:11:20.311757+00, 2025-07-29 18:11:20.311757+00, interval_training_5, CARDIO_INTERVAL, 5, Interval Training Level 5, Level 5 progression for Interval Training, null, null, 5, 500, 250, 375).
  Processing category: Steady State Cardio (ID: CARDIO_STEADY)
    ❌ Failed to create node steady_state_cardio_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (448, 2025-07-29 18:11:20.519371+00, 2025-07-29 18:11:20.519371+00, steady_state_cardio_1, CARDIO_STEADY, 1, Steady State Cardio Level 1, Level 1 progression for Steady State Cardio, null, null, 1, 100, 50, 75).
    ❌ Failed to create node steady_state_cardio_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (449, 2025-07-29 18:11:20.727085+00, 2025-07-29 18:11:20.727085+00, steady_state_cardio_2, CARDIO_STEADY, 2, Steady State Cardio Level 2, Level 2 progression for Steady State Cardio, null, null, 2, 200, 100, 150).
    ❌ Failed to create node steady_state_cardio_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (450, 2025-07-29 18:11:20.934636+00, 2025-07-29 18:11:20.934636+00, steady_state_cardio_3, CARDIO_STEADY, 3, Steady State Cardio Level 3, Level 3 progression for Steady State Cardio, null, null, 3, 300, 150, 225).
    ❌ Failed to create node steady_state_cardio_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (451, 2025-07-29 18:11:21.142945+00, 2025-07-29 18:11:21.142945+00, steady_state_cardio_4, CARDIO_STEADY, 4, Steady State Cardio Level 4, Level 4 progression for Steady State Cardio, null, null, 4, 400, 200, 300).
    ❌ Failed to create node steady_state_cardio_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (452, 2025-07-29 18:11:21.351459+00, 2025-07-29 18:11:21.351459+00, steady_state_cardio_5, CARDIO_STEADY, 5, Steady State Cardio Level 5, Level 5 progression for Steady State Cardio, null, null, 5, 500, 250, 375).
  Processing category: Carry (ID: CARRY)
    ✓ Node exists: carry_1
    ✓ Node exists: carry_2
    ✓ Node exists: carry_3
    ✓ Node exists: carry_4
    ✓ Node exists: carry_5
  Processing category: Coordination (ID: COORDINATION)
    ✓ Node exists: coordination_1
    ✓ Node exists: coordination_2
    ✓ Node exists: coordination_3
    ✓ Node exists: coordination_4
    ✓ Node exists: coordination_5
  Processing category: Core (ID: CORE)
    ✓ Node exists: core_1
    ✓ Node exists: core_2
    ✓ Node exists: core_3
    ✓ Node exists: core_4
    ✓ Node exists: core_5
  Processing category: Dynamic Core (ID: CORE_DYNAMIC)
    ❌ Failed to create node dynamic_core_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (453, 2025-07-29 18:11:23.120264+00, 2025-07-29 18:11:23.120264+00, dynamic_core_1, CORE_DYNAMIC, 1, Dynamic Core Level 1, Level 1 progression for Dynamic Core, null, null, 1, 100, 50, 75).
    ❌ Failed to create node dynamic_core_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (454, 2025-07-29 18:11:23.327982+00, 2025-07-29 18:11:23.327982+00, dynamic_core_2, CORE_DYNAMIC, 2, Dynamic Core Level 2, Level 2 progression for Dynamic Core, null, null, 2, 200, 100, 150).
    ❌ Failed to create node dynamic_core_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (455, 2025-07-29 18:11:23.535782+00, 2025-07-29 18:11:23.535782+00, dynamic_core_3, CORE_DYNAMIC, 3, Dynamic Core Level 3, Level 3 progression for Dynamic Core, null, null, 3, 300, 150, 225).
    ❌ Failed to create node dynamic_core_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (456, 2025-07-29 18:11:23.743264+00, 2025-07-29 18:11:23.743264+00, dynamic_core_4, CORE_DYNAMIC, 4, Dynamic Core Level 4, Level 4 progression for Dynamic Core, null, null, 4, 400, 200, 300).
    ❌ Failed to create node dynamic_core_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (457, 2025-07-29 18:11:23.950597+00, 2025-07-29 18:11:23.950597+00, dynamic_core_5, CORE_DYNAMIC, 5, Dynamic Core Level 5, Level 5 progression for Dynamic Core, null, null, 5, 500, 250, 375).
  Processing category: Rotational Core (ID: CORE_ROTATIONAL)
    ❌ Failed to create node rotational_core_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (458, 2025-07-29 18:11:24.158812+00, 2025-07-29 18:11:24.158812+00, rotational_core_1, CORE_ROTATIONAL, 1, Rotational Core Level 1, Level 1 progression for Rotational Core, null, null, 1, 100, 50, 75).
    ❌ Failed to create node rotational_core_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (459, 2025-07-29 18:11:24.366561+00, 2025-07-29 18:11:24.366561+00, rotational_core_2, CORE_ROTATIONAL, 2, Rotational Core Level 2, Level 2 progression for Rotational Core, null, null, 2, 200, 100, 150).
    ❌ Failed to create node rotational_core_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (460, 2025-07-29 18:11:24.574407+00, 2025-07-29 18:11:24.574407+00, rotational_core_3, CORE_ROTATIONAL, 3, Rotational Core Level 3, Level 3 progression for Rotational Core, null, null, 3, 300, 150, 225).
    ❌ Failed to create node rotational_core_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (461, 2025-07-29 18:11:24.781826+00, 2025-07-29 18:11:24.781826+00, rotational_core_4, CORE_ROTATIONAL, 4, Rotational Core Level 4, Level 4 progression for Rotational Core, null, null, 4, 400, 200, 300).
    ❌ Failed to create node rotational_core_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (462, 2025-07-29 18:11:24.990343+00, 2025-07-29 18:11:24.990343+00, rotational_core_5, CORE_ROTATIONAL, 5, Rotational Core Level 5, Level 5 progression for Rotational Core, null, null, 5, 500, 250, 375).
  Processing category: Static Core (ID: CORE_STATIC)
    ❌ Failed to create node static_core_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (463, 2025-07-29 18:11:25.199272+00, 2025-07-29 18:11:25.199272+00, static_core_1, CORE_STATIC, 1, Static Core Level 1, Level 1 progression for Static Core, null, null, 1, 100, 50, 75).
    ❌ Failed to create node static_core_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (464, 2025-07-29 18:11:25.406746+00, 2025-07-29 18:11:25.406746+00, static_core_2, CORE_STATIC, 2, Static Core Level 2, Level 2 progression for Static Core, null, null, 2, 200, 100, 150).
    ❌ Failed to create node static_core_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (465, 2025-07-29 18:11:25.615283+00, 2025-07-29 18:11:25.615283+00, static_core_3, CORE_STATIC, 3, Static Core Level 3, Level 3 progression for Static Core, null, null, 3, 300, 150, 225).
    ❌ Failed to create node static_core_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (466, 2025-07-29 18:11:25.82328+00, 2025-07-29 18:11:25.82328+00, static_core_4, CORE_STATIC, 4, Static Core Level 4, Level 4 progression for Static Core, null, null, 4, 400, 200, 300).
    ❌ Failed to create node static_core_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (467, 2025-07-29 18:11:26.0315+00, 2025-07-29 18:11:26.0315+00, static_core_5, CORE_STATIC, 5, Static Core Level 5, Level 5 progression for Static Core, null, null, 5, 500, 250, 375).
  Processing category: Flexibility (ID: FLEXIBILITY)
    ✓ Node exists: flexibility_1
    ✓ Node exists: flexibility_2
    ✓ Node exists: flexibility_3
    ✓ Node exists: flexibility_4
    ✓ Node exists: flexibility_5
  Processing category: Flow Movement (ID: FLOW_MOVEMENT)
    ✓ Node exists: flow_movement_1
    ✓ Node exists: flow_movement_2
    ✓ Node exists: flow_movement_3
    ✓ Node exists: flow_movement_4
    ✓ Node exists: flow_movement_5
  Processing category: Grip Strength (ID: GRIP_STRENGTH)
    ❌ Failed to create node grip_strength_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (468, 2025-07-29 18:11:27.279587+00, 2025-07-29 18:11:27.279587+00, grip_strength_1, GRIP_STRENGTH, 1, Grip Strength Level 1, Level 1 progression for Grip Strength, null, null, 1, 100, 50, 75).
    ❌ Failed to create node grip_strength_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (469, 2025-07-29 18:11:27.487185+00, 2025-07-29 18:11:27.487185+00, grip_strength_2, GRIP_STRENGTH, 2, Grip Strength Level 2, Level 2 progression for Grip Strength, null, null, 2, 200, 100, 150).
    ❌ Failed to create node grip_strength_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (470, 2025-07-29 18:11:27.694654+00, 2025-07-29 18:11:27.694654+00, grip_strength_3, GRIP_STRENGTH, 3, Grip Strength Level 3, Level 3 progression for Grip Strength, null, null, 3, 300, 150, 225).
    ❌ Failed to create node grip_strength_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (471, 2025-07-29 18:11:27.902337+00, 2025-07-29 18:11:27.902337+00, grip_strength_4, GRIP_STRENGTH, 4, Grip Strength Level 4, Level 4 progression for Grip Strength, null, null, 4, 400, 200, 300).
    ❌ Failed to create node grip_strength_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (472, 2025-07-29 18:11:28.109732+00, 2025-07-29 18:11:28.109732+00, grip_strength_5, GRIP_STRENGTH, 5, Grip Strength Level 5, Level 5 progression for Grip Strength, null, null, 5, 500, 250, 375).
  Processing category: Handstand Skills (ID: HANDSTAND)
    ❌ Failed to create node handstand_skills_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (473, 2025-07-29 18:11:28.320984+00, 2025-07-29 18:11:28.320984+00, handstand_skills_1, HANDSTAND, 1, Handstand Skills Level 1, Level 1 progression for Handstand Skills, null, null, 1, 100, 50, 75).
    ❌ Failed to create node handstand_skills_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (474, 2025-07-29 18:11:28.54074+00, 2025-07-29 18:11:28.54074+00, handstand_skills_2, HANDSTAND, 2, Handstand Skills Level 2, Level 2 progression for Handstand Skills, null, null, 2, 200, 100, 150).
    ❌ Failed to create node handstand_skills_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (475, 2025-07-29 18:11:28.748877+00, 2025-07-29 18:11:28.748877+00, handstand_skills_3, HANDSTAND, 3, Handstand Skills Level 3, Level 3 progression for Handstand Skills, null, null, 3, 300, 150, 225).
    ❌ Failed to create node handstand_skills_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (476, 2025-07-29 18:11:28.9565+00, 2025-07-29 18:11:28.9565+00, handstand_skills_4, HANDSTAND, 4, Handstand Skills Level 4, Level 4 progression for Handstand Skills, null, null, 4, 400, 200, 300).
    ❌ Failed to create node handstand_skills_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (477, 2025-07-29 18:11:29.165106+00, 2025-07-29 18:11:29.165106+00, handstand_skills_5, HANDSTAND, 5, Handstand Skills Level 5, Level 5 progression for Handstand Skills, null, null, 5, 500, 250, 375).
  Processing category: Hinge (ID: HINGE)
    ✓ Node exists: hinge_1
    ✓ Node exists: hinge_2
    ✓ Node exists: hinge_3
    ✓ Node exists: hinge_4
    ✓ Node exists: hinge_5
  Processing category: Bilateral Hinge (ID: HINGE_BILATERAL)
    ❌ Failed to create node bilateral_hinge_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (478, 2025-07-29 18:11:29.894463+00, 2025-07-29 18:11:29.894463+00, bilateral_hinge_1, HINGE_BILATERAL, 1, Bilateral Hinge Level 1, Level 1 progression for Bilateral Hinge, null, null, 1, 100, 50, 75).
    ❌ Failed to create node bilateral_hinge_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (479, 2025-07-29 18:11:30.102116+00, 2025-07-29 18:11:30.102116+00, bilateral_hinge_2, HINGE_BILATERAL, 2, Bilateral Hinge Level 2, Level 2 progression for Bilateral Hinge, null, null, 2, 200, 100, 150).
    ❌ Failed to create node bilateral_hinge_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (480, 2025-07-29 18:11:30.309665+00, 2025-07-29 18:11:30.309665+00, bilateral_hinge_3, HINGE_BILATERAL, 3, Bilateral Hinge Level 3, Level 3 progression for Bilateral Hinge, null, null, 3, 300, 150, 225).
    ❌ Failed to create node bilateral_hinge_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (481, 2025-07-29 18:11:30.517366+00, 2025-07-29 18:11:30.517366+00, bilateral_hinge_4, HINGE_BILATERAL, 4, Bilateral Hinge Level 4, Level 4 progression for Bilateral Hinge, null, null, 4, 400, 200, 300).
    ❌ Failed to create node bilateral_hinge_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (482, 2025-07-29 18:11:30.725527+00, 2025-07-29 18:11:30.725527+00, bilateral_hinge_5, HINGE_BILATERAL, 5, Bilateral Hinge Level 5, Level 5 progression for Bilateral Hinge, null, null, 5, 500, 250, 375).
  Processing category: Unilateral Hinge (ID: HINGE_UNILATERAL)
    ❌ Failed to create node unilateral_hinge_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (483, 2025-07-29 18:11:30.933661+00, 2025-07-29 18:11:30.933661+00, unilateral_hinge_1, HINGE_UNILATERAL, 1, Unilateral Hinge Level 1, Level 1 progression for Unilateral Hinge, null, null, 1, 100, 50, 75).
    ❌ Failed to create node unilateral_hinge_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (484, 2025-07-29 18:11:31.143858+00, 2025-07-29 18:11:31.143858+00, unilateral_hinge_2, HINGE_UNILATERAL, 2, Unilateral Hinge Level 2, Level 2 progression for Unilateral Hinge, null, null, 2, 200, 100, 150).
    ❌ Failed to create node unilateral_hinge_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (485, 2025-07-29 18:11:31.351649+00, 2025-07-29 18:11:31.351649+00, unilateral_hinge_3, HINGE_UNILATERAL, 3, Unilateral Hinge Level 3, Level 3 progression for Unilateral Hinge, null, null, 3, 300, 150, 225).
    ❌ Failed to create node unilateral_hinge_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (486, 2025-07-29 18:11:31.560132+00, 2025-07-29 18:11:31.560132+00, unilateral_hinge_4, HINGE_UNILATERAL, 4, Unilateral Hinge Level 4, Level 4 progression for Unilateral Hinge, null, null, 4, 400, 200, 300).
    ❌ Failed to create node unilateral_hinge_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (487, 2025-07-29 18:11:31.767705+00, 2025-07-29 18:11:31.767705+00, unilateral_hinge_5, HINGE_UNILATERAL, 5, Unilateral Hinge Level 5, Level 5 progression for Unilateral Hinge, null, null, 5, 500, 250, 375).
  Processing category: Locomotion (ID: LOCOMOTION)
    ✓ Node exists: locomotion_1
    ✓ Node exists: locomotion_2
    ✓ Node exists: locomotion_3
    ✓ Node exists: locomotion_4
    ✓ Node exists: locomotion_5
  Processing category: Plyometrics (Lower) (ID: LOWER_PLYOMETRIC)
    ❌ Failed to create node plyometrics_lower_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (488, 2025-07-29 18:11:32.494578+00, 2025-07-29 18:11:32.494578+00, plyometrics_lower_1, LOWER_PLYOMETRIC, 1, Plyometrics (Lower) Level 1, Level 1 progression for Plyometrics (Lower), null, null, 1, 100, 50, 75).
    ❌ Failed to create node plyometrics_lower_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (489, 2025-07-29 18:11:32.702538+00, 2025-07-29 18:11:32.702538+00, plyometrics_lower_2, LOWER_PLYOMETRIC, 2, Plyometrics (Lower) Level 2, Level 2 progression for Plyometrics (Lower), null, null, 2, 200, 100, 150).
    ❌ Failed to create node plyometrics_lower_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (490, 2025-07-29 18:11:32.910634+00, 2025-07-29 18:11:32.910634+00, plyometrics_lower_3, LOWER_PLYOMETRIC, 3, Plyometrics (Lower) Level 3, Level 3 progression for Plyometrics (Lower), null, null, 3, 300, 150, 225).
    ❌ Failed to create node plyometrics_lower_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (491, 2025-07-29 18:11:33.118936+00, 2025-07-29 18:11:33.118936+00, plyometrics_lower_4, LOWER_PLYOMETRIC, 4, Plyometrics (Lower) Level 4, Level 4 progression for Plyometrics (Lower), null, null, 4, 400, 200, 300).
    ❌ Failed to create node plyometrics_lower_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (492, 2025-07-29 18:11:33.326838+00, 2025-07-29 18:11:33.326838+00, plyometrics_lower_5, LOWER_PLYOMETRIC, 5, Plyometrics (Lower) Level 5, Level 5 progression for Plyometrics (Lower), null, null, 5, 500, 250, 375).
  Processing category: Mobility Flow (ID: MOBILITY_FLOW)
    ✓ Node exists: mobility_flow_1
    ✓ Node exists: mobility_flow_2
    ✓ Node exists: mobility_flow_3
    ✓ Node exists: mobility_flow_4
    ✓ Node exists: mobility_flow_5
  Processing category: Posterior Chain (ID: POSTERIOR_CHAIN)
    ❌ Failed to create node posterior_chain_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (493, 2025-07-29 18:11:34.054668+00, 2025-07-29 18:11:34.054668+00, posterior_chain_1, POSTERIOR_CHAIN, 1, Posterior Chain Level 1, Level 1 progression for Posterior Chain, null, null, 1, 100, 50, 75).
    ❌ Failed to create node posterior_chain_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (494, 2025-07-29 18:11:34.262375+00, 2025-07-29 18:11:34.262375+00, posterior_chain_2, POSTERIOR_CHAIN, 2, Posterior Chain Level 2, Level 2 progression for Posterior Chain, null, null, 2, 200, 100, 150).
    ❌ Failed to create node posterior_chain_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (495, 2025-07-29 18:11:34.470377+00, 2025-07-29 18:11:34.470377+00, posterior_chain_3, POSTERIOR_CHAIN, 3, Posterior Chain Level 3, Level 3 progression for Posterior Chain, null, null, 3, 300, 150, 225).
    ❌ Failed to create node posterior_chain_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (496, 2025-07-29 18:11:34.678345+00, 2025-07-29 18:11:34.678345+00, posterior_chain_4, POSTERIOR_CHAIN, 4, Posterior Chain Level 4, Level 4 progression for Posterior Chain, null, null, 4, 400, 200, 300).
    ❌ Failed to create node posterior_chain_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (497, 2025-07-29 18:11:34.886204+00, 2025-07-29 18:11:34.886204+00, posterior_chain_5, POSTERIOR_CHAIN, 5, Posterior Chain Level 5, Level 5 progression for Posterior Chain, null, null, 5, 500, 250, 375).
  Processing category: Power Endurance (ID: POWER_ENDURANCE)
    ✓ Node exists: power_endurance_1
    ✓ Node exists: power_endurance_2
    ✓ Node exists: power_endurance_3
    ✓ Node exists: power_endurance_4
    ✓ Node exists: power_endurance_5
  Processing category: Pull (ID: PULL)
    ✓ Node exists: pull_1
    ✓ Node exists: pull_2
    ✓ Node exists: pull_3
    ✓ Node exists: pull_4
    ✓ Node exists: pull_5
  Processing category: Horizontal Pulling (ID: PULL_HORIZONTAL)
    ❌ Failed to create node horizontal_pulling_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (498, 2025-07-29 18:11:36.13443+00, 2025-07-29 18:11:36.13443+00, horizontal_pulling_1, PULL_HORIZONTAL, 1, Horizontal Pulling Level 1, Level 1 progression for Horizontal Pulling, null, null, 1, 100, 50, 75).
    ❌ Failed to create node horizontal_pulling_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (499, 2025-07-29 18:11:36.342571+00, 2025-07-29 18:11:36.342571+00, horizontal_pulling_2, PULL_HORIZONTAL, 2, Horizontal Pulling Level 2, Level 2 progression for Horizontal Pulling, null, null, 2, 200, 100, 150).
    ❌ Failed to create node horizontal_pulling_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (500, 2025-07-29 18:11:36.550497+00, 2025-07-29 18:11:36.550497+00, horizontal_pulling_3, PULL_HORIZONTAL, 3, Horizontal Pulling Level 3, Level 3 progression for Horizontal Pulling, null, null, 3, 300, 150, 225).
    ❌ Failed to create node horizontal_pulling_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (501, 2025-07-29 18:11:36.758525+00, 2025-07-29 18:11:36.758525+00, horizontal_pulling_4, PULL_HORIZONTAL, 4, Horizontal Pulling Level 4, Level 4 progression for Horizontal Pulling, null, null, 4, 400, 200, 300).
    ❌ Failed to create node horizontal_pulling_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (502, 2025-07-29 18:11:36.974939+00, 2025-07-29 18:11:36.974939+00, horizontal_pulling_5, PULL_HORIZONTAL, 5, Horizontal Pulling Level 5, Level 5 progression for Horizontal Pulling, null, null, 5, 500, 250, 375).
  Processing category: Unilateral Pulling (ID: PULL_UNILATERAL)
    ❌ Failed to create node unilateral_pulling_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (503, 2025-07-29 18:11:37.182557+00, 2025-07-29 18:11:37.182557+00, unilateral_pulling_1, PULL_UNILATERAL, 1, Unilateral Pulling Level 1, Level 1 progression for Unilateral Pulling, null, null, 1, 100, 50, 75).
    ❌ Failed to create node unilateral_pulling_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (504, 2025-07-29 18:11:37.396028+00, 2025-07-29 18:11:37.396028+00, unilateral_pulling_2, PULL_UNILATERAL, 2, Unilateral Pulling Level 2, Level 2 progression for Unilateral Pulling, null, null, 2, 200, 100, 150).
    ❌ Failed to create node unilateral_pulling_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (505, 2025-07-29 18:11:37.60376+00, 2025-07-29 18:11:37.60376+00, unilateral_pulling_3, PULL_UNILATERAL, 3, Unilateral Pulling Level 3, Level 3 progression for Unilateral Pulling, null, null, 3, 300, 150, 225).
    ❌ Failed to create node unilateral_pulling_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (506, 2025-07-29 18:11:37.812008+00, 2025-07-29 18:11:37.812008+00, unilateral_pulling_4, PULL_UNILATERAL, 4, Unilateral Pulling Level 4, Level 4 progression for Unilateral Pulling, null, null, 4, 400, 200, 300).
    ❌ Failed to create node unilateral_pulling_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (507, 2025-07-29 18:11:38.019654+00, 2025-07-29 18:11:38.019654+00, unilateral_pulling_5, PULL_UNILATERAL, 5, Unilateral Pulling Level 5, Level 5 progression for Unilateral Pulling, null, null, 5, 500, 250, 375).
  Processing category: Vertical Pulling (ID: PULL_VERTICAL)
    ❌ Failed to create node vertical_pulling_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (508, 2025-07-29 18:11:38.227887+00, 2025-07-29 18:11:38.227887+00, vertical_pulling_1, PULL_VERTICAL, 1, Vertical Pulling Level 1, Level 1 progression for Vertical Pulling, null, null, 1, 100, 50, 75).
    ❌ Failed to create node vertical_pulling_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (509, 2025-07-29 18:11:38.435774+00, 2025-07-29 18:11:38.435774+00, vertical_pulling_2, PULL_VERTICAL, 2, Vertical Pulling Level 2, Level 2 progression for Vertical Pulling, null, null, 2, 200, 100, 150).
    ❌ Failed to create node vertical_pulling_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (510, 2025-07-29 18:11:38.643488+00, 2025-07-29 18:11:38.643488+00, vertical_pulling_3, PULL_VERTICAL, 3, Vertical Pulling Level 3, Level 3 progression for Vertical Pulling, null, null, 3, 300, 150, 225).
    ❌ Failed to create node vertical_pulling_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (511, 2025-07-29 18:11:38.852007+00, 2025-07-29 18:11:38.852007+00, vertical_pulling_4, PULL_VERTICAL, 4, Vertical Pulling Level 4, Level 4 progression for Vertical Pulling, null, null, 4, 400, 200, 300).
    ❌ Failed to create node vertical_pulling_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (512, 2025-07-29 18:11:39.059802+00, 2025-07-29 18:11:39.059802+00, vertical_pulling_5, PULL_VERTICAL, 5, Vertical Pulling Level 5, Level 5 progression for Vertical Pulling, null, null, 5, 500, 250, 375).
  Processing category: Push (ID: PUSH)
    ✓ Node exists: push_1
    ✓ Node exists: push_2
    ✓ Node exists: push_3
    ✓ Node exists: push_4
    ✓ Node exists: push_5
  Processing category: Horizontal Pushing (ID: PUSH_HORIZONTAL)
    ❌ Failed to create node horizontal_pushing_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (513, 2025-07-29 18:11:39.787177+00, 2025-07-29 18:11:39.787177+00, horizontal_pushing_1, PUSH_HORIZONTAL, 1, Horizontal Pushing Level 1, Level 1 progression for Horizontal Pushing, null, null, 1, 100, 50, 75).
    ❌ Failed to create node horizontal_pushing_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (514, 2025-07-29 18:11:39.994757+00, 2025-07-29 18:11:39.994757+00, horizontal_pushing_2, PUSH_HORIZONTAL, 2, Horizontal Pushing Level 2, Level 2 progression for Horizontal Pushing, null, null, 2, 200, 100, 150).
    ❌ Failed to create node horizontal_pushing_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (515, 2025-07-29 18:11:40.202356+00, 2025-07-29 18:11:40.202356+00, horizontal_pushing_3, PUSH_HORIZONTAL, 3, Horizontal Pushing Level 3, Level 3 progression for Horizontal Pushing, null, null, 3, 300, 150, 225).
    ❌ Failed to create node horizontal_pushing_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (516, 2025-07-29 18:11:40.409939+00, 2025-07-29 18:11:40.409939+00, horizontal_pushing_4, PUSH_HORIZONTAL, 4, Horizontal Pushing Level 4, Level 4 progression for Horizontal Pushing, null, null, 4, 400, 200, 300).
    ❌ Failed to create node horizontal_pushing_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (517, 2025-07-29 18:11:40.617328+00, 2025-07-29 18:11:40.617328+00, horizontal_pushing_5, PUSH_HORIZONTAL, 5, Horizontal Pushing Level 5, Level 5 progression for Horizontal Pushing, null, null, 5, 500, 250, 375).
  Processing category: Unilateral Pushing (ID: PUSH_UNILATERAL)
    ❌ Failed to create node unilateral_pushing_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (518, 2025-07-29 18:11:40.825265+00, 2025-07-29 18:11:40.825265+00, unilateral_pushing_1, PUSH_UNILATERAL, 1, Unilateral Pushing Level 1, Level 1 progression for Unilateral Pushing, null, null, 1, 100, 50, 75).
    ❌ Failed to create node unilateral_pushing_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (519, 2025-07-29 18:11:41.032791+00, 2025-07-29 18:11:41.032791+00, unilateral_pushing_2, PUSH_UNILATERAL, 2, Unilateral Pushing Level 2, Level 2 progression for Unilateral Pushing, null, null, 2, 200, 100, 150).
    ❌ Failed to create node unilateral_pushing_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (520, 2025-07-29 18:11:41.242558+00, 2025-07-29 18:11:41.242558+00, unilateral_pushing_3, PUSH_UNILATERAL, 3, Unilateral Pushing Level 3, Level 3 progression for Unilateral Pushing, null, null, 3, 300, 150, 225).
    ❌ Failed to create node unilateral_pushing_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (521, 2025-07-29 18:11:41.451013+00, 2025-07-29 18:11:41.451013+00, unilateral_pushing_4, PUSH_UNILATERAL, 4, Unilateral Pushing Level 4, Level 4 progression for Unilateral Pushing, null, null, 4, 400, 200, 300).
    ❌ Failed to create node unilateral_pushing_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (522, 2025-07-29 18:11:41.65886+00, 2025-07-29 18:11:41.65886+00, unilateral_pushing_5, PUSH_UNILATERAL, 5, Unilateral Pushing Level 5, Level 5 progression for Unilateral Pushing, null, null, 5, 500, 250, 375).
  Processing category: Vertical Pushing (ID: PUSH_VERTICAL)
    ❌ Failed to create node vertical_pushing_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (523, 2025-07-29 18:11:41.866884+00, 2025-07-29 18:11:41.866884+00, vertical_pushing_1, PUSH_VERTICAL, 1, Vertical Pushing Level 1, Level 1 progression for Vertical Pushing, null, null, 1, 100, 50, 75).
    ❌ Failed to create node vertical_pushing_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (524, 2025-07-29 18:11:42.074605+00, 2025-07-29 18:11:42.074605+00, vertical_pushing_2, PUSH_VERTICAL, 2, Vertical Pushing Level 2, Level 2 progression for Vertical Pushing, null, null, 2, 200, 100, 150).
    ❌ Failed to create node vertical_pushing_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (525, 2025-07-29 18:11:42.282442+00, 2025-07-29 18:11:42.282442+00, vertical_pushing_3, PUSH_VERTICAL, 3, Vertical Pushing Level 3, Level 3 progression for Vertical Pushing, null, null, 3, 300, 150, 225).
    ❌ Failed to create node vertical_pushing_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (526, 2025-07-29 18:11:42.490228+00, 2025-07-29 18:11:42.490228+00, vertical_pushing_4, PUSH_VERTICAL, 4, Vertical Pushing Level 4, Level 4 progression for Vertical Pushing, null, null, 4, 400, 200, 300).
    ❌ Failed to create node vertical_pushing_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (527, 2025-07-29 18:11:42.703839+00, 2025-07-29 18:11:42.703839+00, vertical_pushing_5, PUSH_VERTICAL, 5, Vertical Pushing Level 5, Level 5 progression for Vertical Pushing, null, null, 5, 500, 250, 375).
  Processing category: Recovery (ID: RECOVERY)
    ✓ Node exists: recovery_1
    ✓ Node exists: recovery_2
    ✓ Node exists: recovery_3
    ✓ Node exists: recovery_4
    ✓ Node exists: recovery_5
  Processing category: Shoulder Stability (ID: SHOULDER_STABILITY)
    ❌ Failed to create node shoulder_stability_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (528, 2025-07-29 18:11:43.431806+00, 2025-07-29 18:11:43.431806+00, shoulder_stability_1, SHOULDER_STABILITY, 1, Shoulder Stability Level 1, Level 1 progression for Shoulder Stability, null, null, 1, 100, 50, 75).
    ❌ Failed to create node shoulder_stability_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (529, 2025-07-29 18:11:43.639362+00, 2025-07-29 18:11:43.639362+00, shoulder_stability_2, SHOULDER_STABILITY, 2, Shoulder Stability Level 2, Level 2 progression for Shoulder Stability, null, null, 2, 200, 100, 150).
    ❌ Failed to create node shoulder_stability_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (530, 2025-07-29 18:11:43.846861+00, 2025-07-29 18:11:43.846861+00, shoulder_stability_3, SHOULDER_STABILITY, 3, Shoulder Stability Level 3, Level 3 progression for Shoulder Stability, null, null, 3, 300, 150, 225).
    ❌ Failed to create node shoulder_stability_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (531, 2025-07-29 18:11:44.05696+00, 2025-07-29 18:11:44.05696+00, shoulder_stability_4, SHOULDER_STABILITY, 4, Shoulder Stability Level 4, Level 4 progression for Shoulder Stability, null, null, 4, 400, 200, 300).
    ❌ Failed to create node shoulder_stability_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (532, 2025-07-29 18:11:44.269763+00, 2025-07-29 18:11:44.269763+00, shoulder_stability_5, SHOULDER_STABILITY, 5, Shoulder Stability Level 5, Level 5 progression for Shoulder Stability, null, null, 5, 500, 250, 375).
  Processing category: Squat (ID: SQUAT)
    ✓ Node exists: squat_1
    ✓ Node exists: squat_2
    ✓ Node exists: squat_3
    ✓ Node exists: squat_4
    ✓ Node exists: squat_5
  Processing category: Bilateral Squats (ID: SQUAT_BILATERAL)
    ❌ Failed to create node bilateral_squats_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (533, 2025-07-29 18:11:45.034007+00, 2025-07-29 18:11:45.034007+00, bilateral_squats_1, SQUAT_BILATERAL, 1, Bilateral Squats Level 1, Level 1 progression for Bilateral Squats, null, null, 1, 100, 50, 75).
    ❌ Failed to create node bilateral_squats_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (534, 2025-07-29 18:11:45.241838+00, 2025-07-29 18:11:45.241838+00, bilateral_squats_2, SQUAT_BILATERAL, 2, Bilateral Squats Level 2, Level 2 progression for Bilateral Squats, null, null, 2, 200, 100, 150).
    ❌ Failed to create node bilateral_squats_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (535, 2025-07-29 18:11:45.450426+00, 2025-07-29 18:11:45.450426+00, bilateral_squats_3, SQUAT_BILATERAL, 3, Bilateral Squats Level 3, Level 3 progression for Bilateral Squats, null, null, 3, 300, 150, 225).
    ❌ Failed to create node bilateral_squats_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (536, 2025-07-29 18:11:45.658398+00, 2025-07-29 18:11:45.658398+00, bilateral_squats_4, SQUAT_BILATERAL, 4, Bilateral Squats Level 4, Level 4 progression for Bilateral Squats, null, null, 4, 400, 200, 300).
    ❌ Failed to create node bilateral_squats_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (537, 2025-07-29 18:11:45.866984+00, 2025-07-29 18:11:45.866984+00, bilateral_squats_5, SQUAT_BILATERAL, 5, Bilateral Squats Level 5, Level 5 progression for Bilateral Squats, null, null, 5, 500, 250, 375).
  Processing category: Unilateral Squats (ID: SQUAT_UNILATERAL)
    ❌ Failed to create node unilateral_squats_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (538, 2025-07-29 18:11:46.074877+00, 2025-07-29 18:11:46.074877+00, unilateral_squats_1, SQUAT_UNILATERAL, 1, Unilateral Squats Level 1, Level 1 progression for Unilateral Squats, null, null, 1, 100, 50, 75).
    ❌ Failed to create node unilateral_squats_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (539, 2025-07-29 18:11:46.282788+00, 2025-07-29 18:11:46.282788+00, unilateral_squats_2, SQUAT_UNILATERAL, 2, Unilateral Squats Level 2, Level 2 progression for Unilateral Squats, null, null, 2, 200, 100, 150).
    ❌ Failed to create node unilateral_squats_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (540, 2025-07-29 18:11:46.496246+00, 2025-07-29 18:11:46.496246+00, unilateral_squats_3, SQUAT_UNILATERAL, 3, Unilateral Squats Level 3, Level 3 progression for Unilateral Squats, null, null, 3, 300, 150, 225).
    ❌ Failed to create node unilateral_squats_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (541, 2025-07-29 18:11:46.703869+00, 2025-07-29 18:11:46.703869+00, unilateral_squats_4, SQUAT_UNILATERAL, 4, Unilateral Squats Level 4, Level 4 progression for Unilateral Squats, null, null, 4, 400, 200, 300).
    ❌ Failed to create node unilateral_squats_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (542, 2025-07-29 18:11:46.911425+00, 2025-07-29 18:11:46.911425+00, unilateral_squats_5, SQUAT_UNILATERAL, 5, Unilateral Squats Level 5, Level 5 progression for Unilateral Squats, null, null, 5, 500, 250, 375).
  Processing category: Dynamic Power (Upper) (ID: UPPER_DYNAMIC)
    ❌ Failed to create node dynamic_power_upper_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (543, 2025-07-29 18:11:47.118968+00, 2025-07-29 18:11:47.118968+00, dynamic_power_upper_1, UPPER_DYNAMIC, 1, Dynamic Power (Upper) Level 1, Level 1 progression for Dynamic Power (Upper), null, null, 1, 100, 50, 75).
    ❌ Failed to create node dynamic_power_upper_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (544, 2025-07-29 18:11:47.326971+00, 2025-07-29 18:11:47.326971+00, dynamic_power_upper_2, UPPER_DYNAMIC, 2, Dynamic Power (Upper) Level 2, Level 2 progression for Dynamic Power (Upper), null, null, 2, 200, 100, 150).
    ❌ Failed to create node dynamic_power_upper_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (545, 2025-07-29 18:11:47.534471+00, 2025-07-29 18:11:47.534471+00, dynamic_power_upper_3, UPPER_DYNAMIC, 3, Dynamic Power (Upper) Level 3, Level 3 progression for Dynamic Power (Upper), null, null, 3, 300, 150, 225).
    ❌ Failed to create node dynamic_power_upper_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (546, 2025-07-29 18:11:47.742013+00, 2025-07-29 18:11:47.742013+00, dynamic_power_upper_4, UPPER_DYNAMIC, 4, Dynamic Power (Upper) Level 4, Level 4 progression for Dynamic Power (Upper), null, null, 4, 400, 200, 300).
    ❌ Failed to create node dynamic_power_upper_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (547, 2025-07-29 18:11:47.94983+00, 2025-07-29 18:11:47.94983+00, dynamic_power_upper_5, UPPER_DYNAMIC, 5, Dynamic Power (Upper) Level 5, Level 5 progression for Dynamic Power (Upper), null, null, 5, 500, 250, 375).
  Processing category: Isometric Holds (Upper) (ID: UPPER_ISOMETRIC)
    ❌ Failed to create node isometric_holds_upper_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (548, 2025-07-29 18:11:48.157676+00, 2025-07-29 18:11:48.157676+00, isometric_holds_upper_1, UPPER_ISOMETRIC, 1, Isometric Holds (Upper) Level 1, Level 1 progression for Isometric Holds (Upper), null, null, 1, 100, 50, 75).
    ❌ Failed to create node isometric_holds_upper_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (549, 2025-07-29 18:11:48.365844+00, 2025-07-29 18:11:48.365844+00, isometric_holds_upper_2, UPPER_ISOMETRIC, 2, Isometric Holds (Upper) Level 2, Level 2 progression for Isometric Holds (Upper), null, null, 2, 200, 100, 150).
    ❌ Failed to create node isometric_holds_upper_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (550, 2025-07-29 18:11:48.573622+00, 2025-07-29 18:11:48.573622+00, isometric_holds_upper_3, UPPER_ISOMETRIC, 3, Isometric Holds (Upper) Level 3, Level 3 progression for Isometric Holds (Upper), null, null, 3, 300, 150, 225).
    ❌ Failed to create node isometric_holds_upper_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (551, 2025-07-29 18:11:48.781403+00, 2025-07-29 18:11:48.781403+00, isometric_holds_upper_4, UPPER_ISOMETRIC, 4, Isometric Holds (Upper) Level 4, Level 4 progression for Isometric Holds (Upper), null, null, 4, 400, 200, 300).
    ❌ Failed to create node isometric_holds_upper_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (552, 2025-07-29 18:11:48.989185+00, 2025-07-29 18:11:48.989185+00, isometric_holds_upper_5, UPPER_ISOMETRIC, 5, Isometric Holds (Upper) Level 5, Level 5 progression for Isometric Holds (Upper), null, null, 5, 500, 250, 375).
  Processing category: Plyometrics (Upper) (ID: UPPER_PLYOMETRIC)
    ❌ Failed to create node plyometrics_upper_1: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (553, 2025-07-29 18:11:49.197452+00, 2025-07-29 18:11:49.197452+00, plyometrics_upper_1, UPPER_PLYOMETRIC, 1, Plyometrics (Upper) Level 1, Level 1 progression for Plyometrics (Upper), null, null, 1, 100, 50, 75).
    ❌ Failed to create node plyometrics_upper_2: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (554, 2025-07-29 18:11:49.405233+00, 2025-07-29 18:11:49.405233+00, plyometrics_upper_2, UPPER_PLYOMETRIC, 2, Plyometrics (Upper) Level 2, Level 2 progression for Plyometrics (Upper), null, null, 2, 200, 100, 150).
    ❌ Failed to create node plyometrics_upper_3: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (555, 2025-07-29 18:11:49.613543+00, 2025-07-29 18:11:49.613543+00, plyometrics_upper_3, UPPER_PLYOMETRIC, 3, Plyometrics (Upper) Level 3, Level 3 progression for Plyometrics (Upper), null, null, 3, 300, 150, 225).
    ❌ Failed to create node plyometrics_upper_4: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (556, 2025-07-29 18:11:49.821466+00, 2025-07-29 18:11:49.821466+00, plyometrics_upper_4, UPPER_PLYOMETRIC, 4, Plyometrics (Upper) Level 4, Level 4 progression for Plyometrics (Upper), null, null, 4, 400, 200, 300).
    ❌ Failed to create node plyometrics_upper_5: null value in column "ascendant_level_required" of relation "skill_tree_nodes" violates not-null constraint
DETAIL:  Failing row contains (557, 2025-07-29 18:11:50.02967+00, 2025-07-29 18:11:50.02967+00, plyometrics_upper_5, UPPER_PLYOMETRIC, 5, Plyometrics (Upper) Level 5, Level 5 progression for Plyometrics (Upper), null, null, 5, 500, 250, 375).
Found 130 movements to redistribute
⚠️  Could not map category ID: 10 for movement: Wide-Grip Push-up
⚠️  Could not map category ID: 10 for movement: Archer Push-up
⚠️  Could not map category ID: 10 for movement: Push-up
⚠️  Could not map category ID: 10 for movement: Diamond Push-up
⚠️  Could not map category ID: 10 for movement: Decline Push-up
⚠️  Could not map category ID: 11 for movement: Neutral-Grip Pull-up
⚠️  Could not map category ID: 11 for movement: Wide-Grip Pull-up
⚠️  Could not map category ID: 11 for movement: Chin-up
⚠️  Could not map category ID: 11 for movement: Pull-up
⚠️  Could not map category ID: 11 for movement: L-Sit Pull-up
⚠️  Could not map category ID: 12 for movement: Jump Squat
⚠️  Could not map category ID: 12 for movement: Goblet Squat
⚠️  Could not map category ID: 12 for movement: Bulgarian Split Squat
⚠️  Could not map category ID: 12 for movement: Pistol Squat
⚠️  Could not map category ID: 13 for movement: Romanian Deadlift
⚠️  Could not map category ID: 13 for movement: Single-Leg Deadlift
⚠️  Could not map category ID: 13 for movement: Good Morning
⚠️  Could not map category ID: 13 for movement: Hip Thrust
⚠️  Could not map category ID: 13 for movement: Nordic Curl
⚠️  Could not map category ID: 14 for movement: Suitcase Carry
⚠️  Could not map category ID: 14 for movement: Farmer's Walk
⚠️  Could not map category ID: 14 for movement: Waiter's Walk
⚠️  Could not map category ID: 14 for movement: Rack Carry
⚠️  Could not map category ID: 14 for movement: Overhead Carry
⚠️  Could not map category ID: 15 for movement: Hollow Body Hold
⚠️  Could not map category ID: 18 for movement: Neutral-Grip Pull-up
⚠️  Could not map category ID: 18 for movement: Wide-Grip Pull-up
⚠️  Could not map category ID: 18 for movement: Chin-up
⚠️  Could not map category ID: 18 for movement: Pull-up
⚠️  Could not map category ID: 18 for movement: L-Sit Pull-up
⚠️  Could not map category ID: 19 for movement: Wide-Grip Pull-up
⚠️  Could not map category ID: 19 for movement: Pull-up
⚠️  Could not map category ID: 19 for movement: Chin-up
⚠️  Could not map category ID: 19 for movement: Neutral-Grip Pull-up
⚠️  Could not map category ID: 19 for movement: L-Sit Pull-up
⚠️  Could not map category ID: 20 for movement: Wide-Grip Pull-up
⚠️  Could not map category ID: 20 for movement: Neutral-Grip Pull-up
⚠️  Could not map category ID: 20 for movement: Pull-up
⚠️  Could not map category ID: 20 for movement: Chin-up
⚠️  Could not map category ID: 20 for movement: L-Sit Pull-up
⚠️  Could not map category ID: 21 for movement: Push-up
⚠️  Could not map category ID: 21 for movement: Archer Push-up
⚠️  Could not map category ID: 21 for movement: Decline Push-up
⚠️  Could not map category ID: 21 for movement: Wide-Grip Push-up
⚠️  Could not map category ID: 21 for movement: Diamond Push-up
⚠️  Could not map category ID: 22 for movement: Push-up
⚠️  Could not map category ID: 22 for movement: Diamond Push-up
⚠️  Could not map category ID: 22 for movement: Archer Push-up
⚠️  Could not map category ID: 22 for movement: Wide-Grip Push-up
⚠️  Could not map category ID: 22 for movement: Decline Push-up
⚠️  Could not map category ID: 23 for movement: Dynamic Power (Upper) - Basic Movement
⚠️  Could not map category ID: 23 for movement: Dynamic Power (Upper) - Intermediate Movement
⚠️  Could not map category ID: 23 for movement: Dynamic Power (Upper) - Advanced Movement
⚠️  Could not map category ID: 24 for movement: Decline Push-up
⚠️  Could not map category ID: 24 for movement: Archer Push-up
⚠️  Could not map category ID: 24 for movement: Push-up
⚠️  Could not map category ID: 24 for movement: Wide-Grip Push-up
⚠️  Could not map category ID: 24 for movement: Diamond Push-up
⚠️  Could not map category ID: 25 for movement: Isometric Holds (Upper) - Intermediate Movement
⚠️  Could not map category ID: 25 for movement: Isometric Holds (Upper) - Basic Movement
⚠️  Could not map category ID: 25 for movement: Isometric Holds (Upper) - Advanced Movement
⚠️  Could not map category ID: 26 for movement: Bulgarian Split Squat
⚠️  Could not map category ID: 26 for movement: Goblet Squat
⚠️  Could not map category ID: 26 for movement: Jump Squat
⚠️  Could not map category ID: 26 for movement: Pistol Squat
⚠️  Could not map category ID: 27 for movement: Jump Squat
⚠️  Could not map category ID: 27 for movement: Bulgarian Split Squat
⚠️  Could not map category ID: 27 for movement: Goblet Squat
⚠️  Could not map category ID: 27 for movement: Pistol Squat
⚠️  Could not map category ID: 28 for movement: Single-Leg Deadlift
⚠️  Could not map category ID: 28 for movement: Good Morning
⚠️  Could not map category ID: 28 for movement: Romanian Deadlift
⚠️  Could not map category ID: 28 for movement: Hip Thrust
⚠️  Could not map category ID: 28 for movement: Nordic Curl
⚠️  Could not map category ID: 29 for movement: Good Morning
⚠️  Could not map category ID: 29 for movement: Romanian Deadlift
⚠️  Could not map category ID: 29 for movement: Hip Thrust
⚠️  Could not map category ID: 29 for movement: Single-Leg Deadlift
⚠️  Could not map category ID: 29 for movement: Nordic Curl
⚠️  Could not map category ID: 30 for movement: Lateral Jump
⚠️  Could not map category ID: 30 for movement: Box Jump
⚠️  Could not map category ID: 30 for movement: Broad Jump
⚠️  Could not map category ID: 30 for movement: Tuck Jump
⚠️  Could not map category ID: 30 for movement: Depth Jump
⚠️  Could not map category ID: 31 for movement: Hollow Body Hold
⚠️  Could not map category ID: 32 for movement: Hollow Body Hold
⚠️  Could not map category ID: 33 for movement: Hollow Body Hold
⚠️  Could not map category ID: 34 for movement: Mobility Flow - Intermediate Movement
⚠️  Could not map category ID: 34 for movement: Mobility Flow - Basic Movement
⚠️  Could not map category ID: 34 for movement: Mobility Flow - Advanced Movement
⚠️  Could not map category ID: 35 for movement: Shoulder Stability - Intermediate Movement
⚠️  Could not map category ID: 35 for movement: Shoulder Stability - Basic Movement
⚠️  Could not map category ID: 35 for movement: Shoulder Stability - Advanced Movement
⚠️  Could not map category ID: 36 for movement: Locomotion - Basic Movement
⚠️  Could not map category ID: 36 for movement: Locomotion - Intermediate Movement
⚠️  Could not map category ID: 36 for movement: Locomotion - Advanced Movement
⚠️  Could not map category ID: 37 for movement: Single-Leg Deadlift
⚠️  Could not map category ID: 37 for movement: Pistol Squat
⚠️  Could not map category ID: 38 for movement: Coordination - Basic Movement
⚠️  Could not map category ID: 38 for movement: Coordination - Intermediate Movement
⚠️  Could not map category ID: 38 for movement: Coordination - Advanced Movement
⚠️  Could not map category ID: 39 for movement: Broad Jump
⚠️  Could not map category ID: 39 for movement: Tuck Jump
⚠️  Could not map category ID: 39 for movement: Lateral Jump
⚠️  Could not map category ID: 39 for movement: Box Jump
⚠️  Could not map category ID: 39 for movement: Depth Jump
⚠️  Could not map category ID: 40 for movement: Power Endurance - Basic Movement
⚠️  Could not map category ID: 40 for movement: Power Endurance - Intermediate Movement
⚠️  Could not map category ID: 40 for movement: Power Endurance - Advanced Movement
⚠️  Could not map category ID: 42 for movement: Grip Strength - Intermediate Movement
⚠️  Could not map category ID: 42 for movement: Grip Strength - Basic Movement
⚠️  Could not map category ID: 42 for movement: Grip Strength - Advanced Movement
⚠️  Could not map category ID: 43 for movement: Posterior Chain - Basic Movement
⚠️  Could not map category ID: 43 for movement: Posterior Chain - Intermediate Movement
⚠️  Could not map category ID: 43 for movement: Posterior Chain - Advanced Movement
⚠️  Could not map category ID: 44 for movement: Recovery - Basic Movement
⚠️  Could not map category ID: 44 for movement: Recovery - Intermediate Movement
⚠️  Could not map category ID: 44 for movement: Recovery - Advanced Movement
⚠️  Could not map category ID: 46 for movement: Interval Training - Intermediate Movement
⚠️  Could not map category ID: 46 for movement: Interval Training - Basic Movement
⚠️  Could not map category ID: 46 for movement: Interval Training - Advanced Movement
⚠️  Could not map category ID: 47 for movement: Handstand Skills - Basic Movement
⚠️  Could not map category ID: 47 for movement: Handstand Skills - Intermediate Movement
⚠️  Could not map category ID: 47 for movement: Handstand Skills - Advanced Movement
⚠️  Could not map category ID: 48 for movement: Bridge Skills - Intermediate Movement
⚠️  Could not map category ID: 48 for movement: Bridge Skills - Basic Movement
⚠️  Could not map category ID: 48 for movement: Bridge Skills - Advanced Movement
⚠️  Could not map category ID: 49 for movement: Flow Movement - Intermediate Movement
⚠️  Could not map category ID: 49 for movement: Flow Movement - Basic Movement
⚠️  Could not map category ID: 49 for movement: Flow Movement - Advanced Movement
Grouped movements into 0 categories

🎉 Redistribution complete! Updated 0 movements across skill tree levels

🔍 Verifying redistribution...

Movements per level by category:
--------------------------------------------------------------------------------

10:
  Level 1: 5 movements (XP: 1.0-1.0, avg: 1.0)

11:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

12:
  Level 1: 5 movements (XP: 0.0-2.0, avg: 1.0)

13:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

14:
  Level 1: 5 movements (XP: 1.0-1.0, avg: 1.0)

15:
  Level 1: 5 movements (XP: 0.0-1.0, avg: 0.2)

16:
  Level 1: 5 movements (XP: 0.0-0.0, avg: 0.0)

17:
  Level 1: 5 movements (XP: 0.0-0.0, avg: 0.0)

18:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

19:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

20:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

21:
  Level 1: 5 movements (XP: 1.0-1.0, avg: 1.0)

22:
  Level 1: 5 movements (XP: 1.0-1.0, avg: 1.0)

23:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

24:
  Level 1: 5 movements (XP: 1.0-1.0, avg: 1.0)

25:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

26:
  Level 1: 5 movements (XP: 0.0-2.0, avg: 1.0)

27:
  Level 1: 5 movements (XP: 0.0-2.0, avg: 1.0)

28:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

29:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

30:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

31:
  Level 1: 5 movements (XP: 0.0-1.0, avg: 0.2)

32:
  Level 1: 5 movements (XP: 0.0-1.0, avg: 0.2)

33:
  Level 1: 5 movements (XP: 0.0-1.0, avg: 0.2)

34:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

35:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

36:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

37:
  Level 1: 5 movements (XP: 0.0-2.0, avg: 0.6)

38:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

39:
  Level 1: 5 movements (XP: 1.0-2.0, avg: 1.2)

40:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

42:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

43:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

44:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

45:
  Level 1: 5 movements (XP: 0.0-0.0, avg: 0.0)

46:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

47:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

48:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

49:
  Level 1: 3 movements (XP: 1.0-2.0, avg: 1.3)

✅ All movements are properly linked to skill tree nodes

✅ Script completed successfully!
🔌 Database connection closed
~/workspace$ 