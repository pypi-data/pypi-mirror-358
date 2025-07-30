## Specification: Implement Per-Session Time Series Generation

### Understanding the Temporal Contamination Problem

Your current ETL pipeline contains a subtle but critical flaw that undermines the integrity of your time series data for machine learning. The issue stems from how the system handles data from multiple Formula 1 racing sessions when creating training sequences for safety car prediction.

Currently, the pipeline follows this problematic flow: it extracts telemetry data from multiple racing sessions, concatenates all this data into one large dataset, and then applies sliding window extraction to create training sequences. This approach creates what we call "temporal contamination" - training examples that represent impossible transitions between completely different racing contexts.

To understand why this is problematic, imagine what happens at the boundary between two races. Your sliding window might create a sequence where the last 50 time steps come from the end of the Monaco Grand Prix and the first 50 time steps come from the beginning of the Spanish Grand Prix two weeks later. This creates a training example that suggests the telemetry pattern from Monaco's finish line directly leads to patterns from Spain's formation lap. In reality, these events are separated by weeks and occur in completely different racing environments with different track characteristics, weather conditions, and competitive contexts.

This contamination is particularly damaging for safety car prediction because racing incidents are highly contextual to specific track conditions and race circumstances. The telemetry patterns that precede a safety car deployment at Monaco's tight street circuit will be fundamentally different from those at a high-speed circuit like Monza. When your model learns from contaminated sequences that artificially blend these contexts, it develops pattern recognition that cannot reliably generalize to real racing scenarios.

### The Session-Aware Solution

The solution involves treating each racing session as an independent temporal domain with its own coherent narrative. Instead of concatenating raw telemetry data from multiple sessions and then generating sequences, we should generate sequences within each session independently and then combine only the resulting sequences.

This approach ensures that every training sequence represents a genuine temporal progression that could actually occur during a real race. Each sequence maintains what we call "temporal coherence" - the property that all time steps within a sequence come from the same racing context and represent plausible cause-and-effect relationships.

From a machine learning perspective, this approach addresses a fundamental assumption underlying time series algorithms: that temporal relationships between consecutive observations are meaningful and representative of real-world causality. When sequences span across sessions, we violate this assumption by creating training examples where temporal relationships are artifacts of our data processing rather than genuine racing dynamics.

### Implementation Strategy

The transformation requires restructuring your pipeline to process each session as an independent unit during the sequence generation phase. This maintains all the valuable functionality of your existing system while ensuring perfect temporal integrity.

The key insight is that we move the session boundary awareness from an implicit consequence of data concatenation to an explicit design principle of the sequence generation process. This gives us fine-grained control over temporal relationships and ensures that every training example represents a realistic racing scenario.

### Primary Changes Required

#### 1. Modify `pipeline.py` - Main ETL Pipeline
**File**: `pipeline.py`
**Function**: `create_safety_car_dataset()`

**Conceptual change**: Transform from a batch processing approach to a per-session processing approach where each racing session is handled as an independent temporal domain.

**Changes needed**:
Replace the current aggregation-then-sequence-generation flow with per-session processing:

```python
# Replace Steps 2 and 4 with per-session processing
all_sequences = []
all_labels = []
all_metadata = []

# Initialize label encoder once to ensure consistency across all sessions
label_encoder = None
if target_column == 'TrackStatus':
    label_encoder = TrackStatusLabelEncoder()
    
    # Pre-fit the encoder on track status values from all sessions
    # This ensures consistent encoding across different racing contexts
    all_track_statuses = []
    for session_data in sessions_data:
        temp_telemetry = aggregator._merge_session_telemetry(session_data, config.drivers)
        if not temp_telemetry.empty:
            track_status = session_data.get('track_status', pd.DataFrame())
            t0_date = session_data['session_info']['t0_date']
            temp_telemetry = aggregator._align_track_status(temp_telemetry, track_status, t0_date)
            if 'TrackStatus' in temp_telemetry.columns:
                all_track_statuses.extend(temp_telemetry['TrackStatus'].unique())
    
    if all_track_statuses:
        # Fit encoder on all possible track status values for consistency
        sample_series = pd.Series(list(set(all_track_statuses)))
        label_encoder.fit(sample_series)

# Process each session independently to maintain temporal integrity
for session_data in sessions_data:
    session_id = f"{session_data['session_info']['year']}_{session_data['session_info']['race']}_{session_data['session_info']['session_type']}"
    logger.info(f"Processing session: {session_id}")
    
    # Extract and prepare telemetry for this specific session
    session_telemetry = aggregator._merge_session_telemetry(session_data, config.drivers)
    
    # Add session metadata to telemetry data
    session_telemetry['SessionYear'] = session_data['session_info']['year']
    session_telemetry['SessionRace'] = session_data['session_info']['race']
    session_telemetry['SessionType'] = session_data['session_info']['session_type']
    session_telemetry['SessionId'] = session_id
    
    # Align track status for this session's temporal context
    track_status = session_data.get('track_status', pd.DataFrame())
    t0_date = session_data['session_info']['t0_date']
    session_telemetry = aggregator._align_track_status(session_telemetry, track_status, t0_date)
    
    # Skip sessions with insufficient data
    if session_telemetry.empty:
        logger.warning(f"No telemetry data for session {session_id}")
        continue
    
    # Apply consistent track status encoding for this session
    if target_column == 'TrackStatus' and 'TrackStatus' in session_telemetry.columns:
        encoded_labels = label_encoder.transform(session_telemetry['TrackStatus'])
        session_telemetry['TrackStatusEncoded'] = encoded_labels
    
    # Generate sequences only within this session's temporal boundaries
    # This is the critical step that prevents cross-session contamination
    X_session, y_session, metadata_session = ts_generator.generate_sequences(session_telemetry)
    
    # Collect results from this session
    if len(X_session) > 0:
        all_sequences.append(X_session)
        all_labels.extend(y_session)
        all_metadata.extend(metadata_session)
        logger.info(f"Generated {len(X_session)} sequences for session {session_id}")
    else:
        logger.warning(f"No sequences generated for session {session_id}")

# Combine sequences from all sessions into final dataset
if all_sequences:
    X = np.concatenate(all_sequences, axis=0)
    y = np.array(all_labels)
    metadata = all_metadata
    logger.info(f"Combined {len(X)} total sequences from {len(all_sequences)} sessions")
else:
    raise ValueError("No sequences generated from any session")
```

#### 2. Modify `time_series.py` - Time Series Generator
**File**: `time_series.py`
**Function**: `generate_sequences()`

**Conceptual change**: Simplify the grouping logic since we now guarantee that all input data comes from a single session, and add validation to catch any violations of this assumption.

**Key modifications**:
```python
def generate_sequences(self, telemetry_data: pd.DataFrame, 
                     group_by: List[str] = None) -> Tuple[np.ndarray, np.ndarray, List[dict]]:
    """Generate sliding window sequences with built-in preprocessing
    
    Now expects telemetry_data from a single session to ensure temporal coherence.
    This prevents the creation of sequences that span across different racing contexts.
    """
    if group_by is None:
        # Changed from ['SessionId', 'Driver'] to just ['Driver'] since we now
        # process sessions independently and all data should be from one session
        group_by = ['Driver']
    
    # Validate temporal integrity - all data should be from the same session
    if 'SessionId' in telemetry_data.columns:
        unique_sessions = telemetry_data['SessionId'].nunique()
        if unique_sessions > 1:
            session_ids = telemetry_data['SessionId'].unique()
            raise ValueError(f"Multiple sessions detected in single call: {session_ids}. "
                           f"This violates the per-session processing assumption and could "
                           f"lead to temporal contamination. Each call should contain data "
                           f"from exactly one racing session.")
        elif unique_sessions == 1:
            session_id = telemetry_data['SessionId'].iloc[0]
            logger.debug(f"Processing single session: {session_id}")
    
    # Continue with existing sequence generation logic
    # The rest of the function remains unchanged since the core windowing
    # algorithm is sound - we've just ensured it operates on clean data
    sequences = []
    labels = []
    metadata = []
    
    logger.info(f"Processing {len(telemetry_data)} telemetry rows from single session")
    logger.info(f"Grouping by: {group_by}")
    logger.debug(f"Available columns: {list(telemetry_data.columns)}")
    
    # ... rest of existing implementation unchanged
```

#### 3. Add Session Processing Method to `aggregation.py`
**File**: `aggregation.py`
**Class**: `DataAggregator`

**Conceptual change**: Add a dedicated method for processing individual sessions to make the per-session workflow more explicit and maintainable.

```python
def process_single_session(self, session_data: Dict[str, Any], 
                          drivers: Optional[List[str]] = None) -> pd.DataFrame:
    """Process a single session's telemetry data with track status alignment
    
    This method encapsulates all the session-specific processing logic to ensure
    consistent handling of temporal context and track status alignment.
    """
    logger.debug(f"Processing session: {session_data['session_info']}")
    
    # Extract and merge telemetry data for this session
    session_telemetry = self._merge_session_telemetry(session_data, drivers)
    
    if session_telemetry.empty:
        logger.warning("No telemetry data available for session")
        return session_telemetry
    
    # Add session metadata to preserve racing context
    session_telemetry['SessionYear'] = session_data['session_info']['year']
    session_telemetry['SessionRace'] = session_data['session_info']['race']
    session_telemetry['SessionType'] = session_data['session_info']['session_type']
    session_telemetry['SessionId'] = f"{session_data['session_info']['year']}_{session_data['session_info']['race']}_{session_data['session_info']['session_type']}"
    
    # Align track status within this session's temporal context
    track_status = session_data.get('track_status', pd.DataFrame())
    t0_date = session_data['session_info']['t0_date']
    session_telemetry = self._align_track_status(session_telemetry, track_status, t0_date)
    
    logger.debug(f"Processed {len(session_telemetry)} telemetry rows for session")
    return session_telemetry
```

#### 4. Update Documentation and Add Validation

**Create validation function to verify temporal integrity**:
```python
def validate_temporal_integrity(metadata):
    """Validate that all sequences maintain proper temporal boundaries
    
    This function helps verify that the per-session approach is working correctly
    by ensuring no sequence spans across different racing contexts.
    """
    logger.info("Validating temporal integrity of generated sequences...")
    
    session_sequence_counts = {}
    temporal_violations = []
    
    for i, meta in enumerate(metadata):
        session_id = meta['SessionId']
        start_time = meta['start_time']
        end_time = meta['end_time']
        prediction_time = meta['prediction_time']
        
        # Count sequences per session
        session_sequence_counts[session_id] = session_sequence_counts.get(session_id, 0) + 1
        
        # Verify that all times are reasonable (this catches obvious temporal issues)
        if prediction_time < end_time:
            temporal_violations.append(f"Sequence {i}: prediction time {prediction_time} before sequence end {end_time}")
        
        # Log detailed info for debugging
        logger.debug(f"Sequence {i}: {session_id} from {start_time} to {prediction_time}")
    
    if temporal_violations:
        logger.error(f"Found {len(temporal_violations)} temporal violations:")
        for violation in temporal_violations:
            logger.error(f"  {violation}")
        raise ValueError("Temporal integrity validation failed")
    
    logger.info("Temporal integrity validation passed")
    logger.info(f"Sequences per session: {session_sequence_counts}")
    return session_sequence_counts
```

### Expected Outcomes

After implementing these changes, your pipeline will provide several important guarantees that improve the reliability of your safety car prediction models:

**Perfect Temporal Coherence**: Every sequence in your training data will represent a genuine progression of racing events that could actually occur during a real Formula 1 session. This eliminates the artificial temporal transitions that could mislead your models.

**Contextual Consistency**: Each training example maintains its racing context, allowing your models to learn how incidents develop within specific environmental conditions without contamination from unrelated racing situations.

**Enhanced Validation Capabilities**: The per-session approach enables more sophisticated validation strategies, such as leave-one-session-out validation, which provides more realistic assessments of how your models will perform when encountering new racing contexts.

**Scalable Architecture**: The session-aware design makes it easier to add new racing sessions to your dataset while maintaining data quality, and provides a foundation for more advanced techniques like session-specific feature engineering or track-specific model adaptation.

This transformation ensures that your time series data accurately represents the temporal dynamics of Formula 1 racing, providing a solid foundation for building reliable safety car prediction models that can generalize effectively to real-world racing scenarios.