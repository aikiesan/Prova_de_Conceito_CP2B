#!/usr/bin/env python3
"""
Fix AVES Biogas calculation error - divide all AVES values by 3
The AVES biogas values in the database are currently triple what they should be.
"""

import sqlite3
from pathlib import Path

def fix_aves_biogas_calculation():
    """Fix the AVES biogas calculation error by dividing all values by 3"""
    
    # Database path
    db_path = Path(__file__).resolve().parent / "data" / "database.db"
    
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return False
    
    print(f"Fixing AVES biogas calculation in: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, check current AVES values to see the scope of the fix
        cursor.execute("SELECT COUNT(*) as total, SUM(biogas_aves_nm_ano) as sum_before FROM municipios WHERE biogas_aves_nm_ano > 0")
        stats_before = cursor.fetchone()
        total_municipalities_with_aves = stats_before[0] if stats_before[0] else 0
        sum_before = stats_before[1] if stats_before[1] else 0
        
        print(f"Found {total_municipalities_with_aves} municipalities with AVES biogas data")
        print(f"Current total AVES biogas: {sum_before:,.0f} Nm3/ano")
        print(f"After correction will be: {sum_before/3:,.0f} Nm3/ano")
        
        # Apply the fix: Divide all AVES biogas values by 3
        update_sql = """
        UPDATE municipios 
        SET biogas_aves_nm_ano = biogas_aves_nm_ano / 3.0
        WHERE biogas_aves_nm_ano > 0
        """
        
        cursor.execute(update_sql)
        rows_affected = cursor.rowcount
        
        print(f"Fixed AVES values in {rows_affected} municipalities")
        
        # Recalculate total_pecuaria_nm_ano (sum of all livestock biogas)
        recalc_pecuaria_sql = """
        UPDATE municipios 
        SET total_pecuaria_nm_ano = 
            COALESCE(biogas_bovinos_nm_ano, 0) + 
            COALESCE(biogas_suino_nm_ano, 0) + 
            COALESCE(biogas_aves_nm_ano, 0) + 
            COALESCE(biogas_piscicultura_nm_ano, 0)
        """
        
        cursor.execute(recalc_pecuaria_sql)
        print(f"Recalculated total_pecuaria_nm_ano for all municipalities")
        
        # Recalculate total_final_nm_ano (sum of all sources)
        recalc_total_sql = """
        UPDATE municipios 
        SET total_final_nm_ano = 
            COALESCE(total_agricola_nm_ano, 0) + 
            COALESCE(total_pecuaria_nm_ano, 0) + 
            COALESCE(silvicultura_nm_ano, 0) +
            COALESCE(rsu_potencial_nm_habitante_ano, 0) + 
            COALESCE(rpo_potencial_nm_habitante_ano, 0)
        """
        
        cursor.execute(recalc_total_sql)
        print(f"Recalculated total_final_nm_ano for all municipalities")
        
        # Verify the changes
        cursor.execute("SELECT COUNT(*) as total, SUM(biogas_aves_nm_ano) as sum_after FROM municipios WHERE biogas_aves_nm_ano > 0")
        stats_after = cursor.fetchone()
        sum_after = stats_after[1] if stats_after[1] else 0
        
        cursor.execute("SELECT SUM(total_final_nm_ano) as total_final_after FROM municipios")
        total_final_after = cursor.fetchone()[0]
        
        # Commit changes
        conn.commit()
        
        print(f"\nVERIFICATION:")
        print(f"   - AVES biogas before: {sum_before:,.0f} Nm3/ano")
        print(f"   - AVES biogas after: {sum_after:,.0f} Nm3/ano") 
        print(f"   - Reduction: {sum_before - sum_after:,.0f} Nm3/ano")
        print(f"   - Reduction factor: {sum_before/sum_after:.2f}x")
        print(f"   - New total final biogas: {total_final_after:,.0f} Nm3/ano")
        
        # Close connection
        conn.close()
        
        print(f"\nAVES biogas calculation correction completed successfully!")
        print(f"Database updated: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"Error fixing AVES calculation: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("CP2B - AVES Biogas Calculation Fix")
    print("=" * 40)
    
    # Apply the fix
    success = fix_aves_biogas_calculation()
    
    if success:
        print(f"\nFix completed! The AVES biogas values have been corrected.")
    else:
        print(f"\nFix failed! Please check the error messages above.")