Could data science be a useful tool to plan an efficient training routine for speedcubers?

# 1. Problem Statement

The objective of this project is to analyze long-term speedcubing performance using timestamped solve data in order to identify factors influencing performance improvements. 

The core question is:

Which measurable behavioral and temporal factors have the strongest impact on solve time reduction and sub-X probability?

# 2. System Overview

# 3. Data Model

The system requires a dataset containing:
- Timestamp of activity: Date and hour of each solve in the form:  dd/mm/yyyy  hh:mm
- Performance metric in the form: hh:mm:ss

# 4. Definitions

### Sub-X
A solution that take less than X time. Example: 8.00 and 8.93 are classified as sub-9, but 9.00 is sub-10.

### Session
A session is defined as a maximal sequence of consecutive solves in which the time difference between two adjacent solves does not exceed `SESSION_GAP_MAX_SEC`, typically 5 minutes.

# 5. Performance Factors Under Investigation

Performance may be influenced by the following categories:

### 5.1 Temporal Factors
- Time of day (circadian rhythm influence)
- Day of week (routine stability)
- Seasonal variation
- Yearly macro-trend progression

### 5.2 Training Volume Factors
- Total solves per session
- Total solves per day
- Weekly solve frequency
- Rolling training density

### 5.3 Session Structure
- Session size
- Position within session
- Intra-session fatigue effects
  

# 6. Derived Features
From raw timestamps, the following variables are extracted:

- Hour of day
- Day of week
- Month
- Year
- Session size
- Session duration
- Rolling 7-day solve count
- Rolling 30-day solve count


# 7. Visualization & Statistical Methods

The following visualization methods are used:

- Scatter plots
- Line trends through linear regression
- Histograms
- Heatmaps
- Bar plots

Linear regression is used to estimate trend slopes and directional effects.

# 8. Case Study: Personal Dataset
it was applied to a dataset of 70,000+ speedcubing solves recorded since 2018.


## Conclusion
Frequency, solves per year
Session size

# 9. Limitations

The analytical framework relies exclusively on timestamped performance data. Several potentially relevant variables are not recorded and therefore cannot be incorporated into the analysis.

## 9.1 Unobserved Behavioral Factors

Psychological and physiological states may significantly influence performance but are not captured in the dataset. These include:

- Mood and stress levels
- Fatigue and sleep quality
- Cognitive focus and distraction
- Motivation variability

Since these variables are not quantified, their influence cannot be isolated or controlled for in the statistical analysis.

## 9.2 Equipment-Related Factors

Performance may vary depending on hardware characteristics, which are not tracked in the dataset:

- Cube model (magnetic vs non-magnetic)
- Mechanical condition
- Lubrication type and quality
- Wear over time

Without metadata regarding equipment configuration, performance differences 
attributed to hardware changes cannot be distinguished from skill progression.

## 9.3 Environmental Conditions

External conditions may introduce variability, including:

- Lighting conditions
- Ambient temperature
- Noise levels
- Ergonomic setup

These factors are not recorded and may contribute to unexplained variance.

## 9.4 Visual and Perceptual Factors

As a colorblind solver, color contrast and cube color scheme may influence recognition speed and execution efficiency. Since color configuration and solve-specific visual parameters are not logged, this effect cannot be modeled.

## 9.5 Model Constraints

The system uses threshold-based session segmentation and linear regression for trend estimation. These simplifications may not capture nonlinear learning dynamics or complex interaction effects.
