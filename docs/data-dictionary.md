# Data Dictionary

Complete field definitions and relationships for all KBA datasets processed by the pipeline.

## Dataset Overview

| Dataset | German Name | English Description | Records | Date Format |
|---------|-------------|---------------------|---------|-------------|
| FZ-8.2 | Bestand nach Marken | Monthly brand statistics | 2,950 | YYYYMM |
| FZ-8.3 | Fahrzeuganalyse | Vehicle analysis | 21,821 | YYYYMM |
| FZ-8.6 | Regionale Verteilung | Regional distribution | 937 | YYYYMM |
| FZ-8.7 | Alters-/Nutzungsanalyse | Age/usage analysis | 2,954 | YYYYMM |
| FZ-8.8 | Motorisierung | Engine specifications | 1,025 | YYYYMM |
| FZ-8.9 | Nutzfahrzeuge | Commercial vehicles | 2,950 | YYYYMM |
| FZ-8.16 | Sonderkategorien | Special categories | 2,113 | YYYYMM |
| FZ-1.1 | Regionale Fahrzeugdaten | Regional vehicle data | 2,397 | YYYY |
| FZ-1.2 | Verwaltungsaufschlüsselung | Administrative breakdown | 2,397 | YYYY |
| FZ-10.1 | Marken-/Modellanalyse | Brand/model analysis | 22,683 | YYYYMM |
| FZ-2.2 | Kraftstoffart-Zulassungen | Fuel type registrations | 77,913 | YYYY |
| FZ-2.4 | Regionale Metriken | Regional metrics | 77,870 | YYYY |
| FZ-3.1 | Nutzfahrzeuge | Commercial vehicles | 64,657 | YYYY |

## Core Field Definitions

### Common Fields

#### DATE
- **German**: Datum/Zeitraum
- **Data Type**: String
- **Format**: YYYYMM (FZ-8, FZ-10) or YYYY (FZ-1, FZ-2, FZ-3)
- **Description**: Registration period identifier
- **Business Rules**:
  - FZ-8/FZ-10: Must match pattern `^[0-9]{6}$` (e.g., "202312")
  - FZ-1/FZ-2/FZ-3: Must match pattern `^[0-9]{4}$` (e.g., "2023")
  - Cannot be future date
  - Must be within valid range (2020-2030)
- **Example Values**: "202312", "2023"

#### MARKE
- **German**: Marke/Hersteller
- **Data Type**: String
- **Max Length**: 50
- **Description**: Vehicle brand/manufacturer name
- **Business Rules**:
  - Must exist in trade_names reference table
  - Standardized capitalization (UPPERCASE)
  - No leading/trailing spaces
- **Example Values**: "VOLKSWAGEN", "BMW", "MERCEDES-BENZ"

#### ANZAHL
- **German**: Anzahl
- **Data Type**: Integer
- **Description**: Number of vehicle registrations
- **Business Rules**:
  - Must be non-negative (≥ 0)
  - Reasonable upper limit (≤ 100,000 for monthly data)
  - Outliers flagged for manual review
- **Example Values**: 1542, 0, 25678

### FZ-8 Specific Fields

#### FZ-8.2 (Monthly Brand Statistics)
```yaml
fields:
  DATE: {format: "YYYYMM", description: "Month of registration"}
  MARKE: {description: "Vehicle brand"}
  ANZAHL: {description: "Number of new registrations"}
  BESTAND: {description: "Total vehicle stock", data_type: "integer"}
  ANTEIL_PROZENT: {description: "Market share percentage", data_type: "decimal(5,2)"}
```

#### FZ-8.3 (Vehicle Analysis)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  FAHRZEUGKLASSE: {description: "Vehicle class (PKW, LKW, etc.)", values: ["PKW", "LKW", "KRAFTRAD", "SONSTIGE"]}
  KRAFTSTOFF: {description: "Fuel type", values: ["BENZIN", "DIESEL", "ELEKTRO", "HYBRID", "PLUG-IN", "SONSTIGE"]}
  HUBRAUM_KLASSE: {description: "Engine displacement class", data_type: "string"}
  ANZAHL: {description: "Registration count"}
```

#### FZ-8.6 (Regional Distribution)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  BUNDESLAND: {description: "Federal state", data_type: "string", max_length: 30}
  KREIS: {description: "District/county", data_type: "string", max_length: 50}
  ANZAHL_ZULASSUNGEN: {description: "New registrations"}
  ANZAHL_AUSSERBETRIEB: {description: "Deregistrations"}
  BESTAND: {description: "Total active vehicles"}
```

#### FZ-8.7 (Age/Usage Analysis)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  ALTERSKLASSE: {description: "Age group", values: ["0-1", "1-2", "2-5", "5-10", "10+"]}
  NUTZUNGSART: {description: "Usage type", values: ["PRIVAT", "GEWERBLICH", "BEHÖRDE"]}
  LAUFLEISTUNG_KM: {description: "Mileage range", data_type: "string"}
  ANZAHL: {description: "Vehicle count"}
```

#### FZ-8.8 (Engine Specifications)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  MOTORART: {description: "Engine type", values: ["VERBRENNUNGSMOTOR", "ELEKTROMOTOR", "HYBRID"]}
  HUBRAUM_CCM: {description: "Engine displacement in ccm", data_type: "integer"}
  LEISTUNG_KW: {description: "Engine power in kW", data_type: "integer"}
  EMISSIONSKLASSE: {description: "Emission standard", values: ["EURO_6", "EURO_5", "EURO_4", "SONSTIGE"]}
  ANZAHL: {description: "Vehicle count"}
```

#### FZ-8.9 (Commercial Vehicles)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  FAHRZEUGTYP: {description: "Commercial vehicle type"}
  NUTZLAST_KG: {description: "Payload capacity in kg", data_type: "integer"}
  GESAMTGEWICHT_KG: {description: "Total weight in kg", data_type: "integer"}
  AUFBAUART: {description: "Body type/configuration", data_type: "string"}
  ANZAHL: {description: "Registration count"}
```

#### FZ-8.16 (Special Categories)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  SONDERKATEGORIE: {description: "Special vehicle category"}
  VERWENDUNGSZWECK: {description: "Purpose of use", data_type: "string"}
  GENEHMIGUNGSART: {description: "Approval type", data_type: "string"}
  ANZAHL: {description: "Vehicle count"}
```

### FZ-1 Specific Fields

#### FZ-1.1 (Regional Vehicle Data)
```yaml
fields:
  DATE: {format: "YYYY", description: "Registration year"}
  LAND: {description: "Federal state", data_type: "string", max_length: 30}
  FAHRZEUGKLASSE: {description: "Vehicle class"}
  ANZAHL_BESTAND: {description: "Total vehicle stock", data_type: "integer"}
  ANZAHL_NEUZULASSUNGEN: {description: "New registrations", data_type: "integer"}
  EINWOHNER: {description: "Population count", data_type: "integer"}
  DICHTE_PRO_1000: {description: "Vehicles per 1000 inhabitants", data_type: "decimal(8,2)"}
```

#### FZ-1.2 (Administrative Breakdown)
```yaml
fields:
  DATE: {format: "YYYY"}
  LAND: {description: "Federal state"}
  REGIERUNGSBEZIRK: {description: "Administrative district", data_type: "string"}
  LANDKREIS: {description: "County", data_type: "string"}
  GEMEINDE: {description: "Municipality", data_type: "string"}
  ANZAHL: {description: "Vehicle count"}
```

### FZ-2 Specific Fields

#### FZ-2.2 (Fuel Type Registrations)
```yaml
fields:
  DATE: {format: "YYYY"}
  KRAFTSTOFF: {description: "Fuel type", values: ["BENZIN", "DIESEL", "ELEKTRO", "HYBRID_BENZIN", "HYBRID_DIESEL", "PLUG_IN_HYBRID", "ERDGAS", "AUTOGAS", "WASSERSTOFF", "SONSTIGE"]}
  FAHRZEUGKLASSE: {description: "Vehicle class"}
  ANZAHL_NEUZULASSUNGEN: {description: "New registrations"}
  ANZAHL_BESTAND: {description: "Total stock"}
  ANTEIL_NEUZULASSUNGEN: {description: "Share of new registrations", data_type: "decimal(5,2)"}
  ANTEIL_BESTAND: {description: "Share of total stock", data_type: "decimal(5,2)"}
```

#### FZ-2.4 (Regional Fuel Metrics)
```yaml
fields:
  DATE: {format: "YYYY"}
  LAND: {description: "Federal state"}
  KRAFTSTOFF: {description: "Fuel type"}
  ANZAHL: {description: "Registration count"}
  ANTEIL_REGIONAL: {description: "Regional share", data_type: "decimal(5,2)"}
```

### FZ-3 Specific Fields

#### FZ-3.1 (Commercial Vehicles)
```yaml
fields:
  DATE: {format: "YYYY"}
  FAHRZEUGTYP: {description: "Commercial vehicle type", values: ["LKW", "SATTELZUGMASCHINE", "ANHÄNGER", "AUFLIEGER", "ZUGMASCHINE", "SONSTIGE"]}
  GEWICHTSKLASSE: {description: "Weight class", data_type: "string"}
  VERWENDUNGSZWECK: {description: "Purpose", values: ["GÜTERVERKEHR", "PERSONENVERKEHR", "LAND_FORSTWIRTSCHAFT", "SONSTIGE"]}
  ANZAHL_BESTAND: {description: "Total stock"}
  ANZAHL_NEUZULASSUNGEN: {description: "New registrations"}
  DURCHSCHNITTSALTER: {description: "Average age in years", data_type: "decimal(4,1)"}
```

### FZ-10 Specific Fields

#### FZ-10.1 (Brand/Model Analysis)
```yaml
fields:
  DATE: {format: "YYYYMM"}
  MARKE: {description: "Vehicle brand"}
  MODELLREIHE: {description: "Model series", data_type: "string", max_length: 100}
  FAHRZEUGKLASSE: {description: "Vehicle class"}
  KRAFTSTOFF: {description: "Fuel type"}
  ANZAHL_NEUZULASSUNGEN: {description: "New registrations"}
  MARKTANTEIL_MARKE: {description: "Brand market share", data_type: "decimal(5,2)"}
  MARKTANTEIL_MODELL: {description: "Model market share", data_type: "decimal(5,2)"}
  PREIS_DURCHSCHNITT: {description: "Average price in EUR", data_type: "decimal(10,2)"}
```

### Reference Tables

#### Trade Names (Handelsnamen)
```yaml
fields:
  HSN: {description: "Manufacturer code", data_type: "string", max_length: 10}
  TSN: {description: "Type code", data_type: "string", max_length: 10}
  MARKE: {description: "Brand name", data_type: "string", max_length: 50}
  HANDELSNAME: {description: "Commercial name", data_type: "string", max_length: 100}
  GUELTIG_VON: {description: "Valid from date", data_type: "date"}
  GUELTIG_BIS: {description: "Valid until date", data_type: "date"}
```

#### Model Series (Modellreihen)
```yaml
fields:
  MARKE: {description: "Brand name"}
  MODELLREIHE: {description: "Model series"}
  FAHRZEUGKLASSE: {description: "Vehicle class"}
  SEGMENT: {description: "Market segment", values: ["KLEIN", "KOMPAKT", "MITTEL", "OBER", "LUXUS", "SUV", "VAN"]}
  PRODUKTIONSJAHR_VON: {description: "Production start year", data_type: "integer"}
  PRODUKTIONSJAHR_BIS: {description: "Production end year", data_type: "integer"}
```

## Data Quality Rules

### Validation Rules by Field Type

#### Date Fields
```sql
-- FZ-8/FZ-10 date validation
CHECK (DATE ~ '^[0-9]{6}$' AND DATE::integer BETWEEN 202001 AND 202512)

-- FZ-1/FZ-2/FZ-3 date validation  
CHECK (DATE ~ '^[0-9]{4}$' AND DATE::integer BETWEEN 2020 AND 2030)
```

#### Count Fields
```sql
-- All count fields must be non-negative
CHECK (ANZAHL >= 0)
CHECK (ANZAHL_NEUZULASSUNGEN >= 0)
CHECK (ANZAHL_BESTAND >= 0)

-- Reasonable upper limits
CHECK (ANZAHL <= 100000)  -- Monthly data
CHECK (ANZAHL_NEUZULASSUNGEN <= 1000000)  -- Annual data
```

#### Percentage Fields
```sql
-- Percentage fields must be between 0 and 100
CHECK (ANTEIL_PROZENT BETWEEN 0 AND 100)
CHECK (MARKTANTEIL_MARKE BETWEEN 0 AND 100)
```

#### Reference Integrity
```sql
-- Brand names must exist in reference table
FOREIGN KEY (MARKE) REFERENCES trade_names(MARKE)

-- Model series must exist for given brand
FOREIGN KEY (MARKE, MODELLREIHE) REFERENCES model_series(MARKE, MODELLREIHE)
```

## Business Rules

### Cross-Field Validation
- **Stock vs. New Registrations**: `ANZAHL_BESTAND >= ANZAHL_NEUZULASSUNGEN`
- **Market Share Consistency**: Sum of brand market shares ≤ 100% per period
- **Regional Totals**: Sum of regional data = national total
- **Fuel Type Completeness**: All major fuel types represented

### Temporal Consistency
- **Sequential Months**: No gaps in monthly data series
- **Year-over-Year Growth**: Reasonable growth rates (-50% to +100%)
- **Seasonal Patterns**: Expected seasonal variations in registrations

### Data Completeness
- **Required Fields**: No null values in primary keys and counts
- **Optional Fields**: Null values allowed for descriptive fields
- **Reference Completeness**: All codes must have corresponding descriptions

---

This data dictionary provides the complete field definitions and business rules for all datasets in the KBA Market Analysis pipeline. Use this as the authoritative reference for data validation, transformation logic, and business intelligence queries. 