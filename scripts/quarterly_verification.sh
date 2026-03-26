#!/bin/bash

# Quarterly Security Verification Script
# Runs automated checks for PII, SRI, and external links

LOG_DIR="/Users/kaypumps/Documents/zironsec/docs/operations/Compliance/Fedramp/2026-03-25_Audit_Cycle/03_Verification"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/quarterly_verification_$DATE.log"

echo "Starting quarterly verification on $DATE" > "$LOG_FILE"

# 1. PII Scan
echo "=== PII Scan ===" >> "$LOG_FILE"
grep -rE "(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b|\b\+?[0-9][0-9\-\s]{7,}\b)" ../src/ >> "$LOG_FILE" 2>&1 || echo "No PII found" >> "$LOG_FILE"

# 2. External Links Check
echo "=== External Links Check ===" >> "$LOG_FILE"
grep -r "target=\"_blank\"" ../src/Website/*.html | grep -v "rel=\"noopener noreferrer\"" >> "$LOG_FILE" 2>&1 || echo "All external links secure" >> "$LOG_FILE"

# 3. SRI Check (basic - check if integrity present)
echo "=== SRI Check ===" >> "$LOG_FILE"
grep -r "integrity=" ../src/Website/index.html >> "$LOG_FILE" 2>&1 || echo "SRI not found" >> "$LOG_FILE"

echo "Verification complete. Check $LOG_FILE" >> "$LOG_FILE"