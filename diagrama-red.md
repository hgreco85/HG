```mermaid
flowchart LR
    subgraph GIS [GIS / Nexus]
        A["Alta objeto en Nexus - Trafo / Medidor / Poste"]
        B["Envía ID único (ID GIS)"]
        C["Genera UT en SAP PM"]
    end

    subgraph PS [SAP PS / FI-AA]
        D["Proyecto con materiales y baremos"]
        E["Transacción Z genera Activo fijo"]
        F["Activo fijo crea Equipo en PM"]
        G["Equipo recibe ID de negocio (ej: nro medidor)"]
    end

    subgraph PM [SAP PM]
        H["UT creada en PM con ID GIS"]
        I["Equipo en PM con ID negocio + Activo"]
        J["Proceso Z de vinculación"]
        K["Equipo asignado automáticamente a UT (TPLNR)"]
    end

    subgraph ZTAB [Tabla de correspondencia Z]
        L["ID GIS <-> ID negocio <-> UT <-> Equipo <-> Activo"]
    end

    %% Flujo GIS
    A --> B --> C --> H
    H --> L

    %% Flujo PS
    D --> E --> F --> G --> I
    I --> L

    %% Vinculación
    L --> J --> K
```
