# Agents.py
### Et bibliotek til __Python Mode for Processing__ som implementerer klasser til brug i agent-baseret modellering.

## Oversigt
Bibliotekets formål er at give mulighed for at lave en NetLogo-lignende brugergrænseflade i Processing, som kan skrives kun ved kendskab til Python. Biblioteket giver ikke kun muligheden for at kode agenternes opførsel, men gør det også muligt at tilføje knapper til brugergrænsefladen, som så kan bruges til at styre modellen dynamisk.

## Model
`Model` er den centrale klasse for biblioteket. Klassens constructor tager følgende argumenter:

  * __N__: Antallet af _agenter_ som modellen har til at begynde med.
  * __nTiles__: Antallet af _tiles_ på hvert led. Modellen vil derfor indeholde i alt `nTiles * nTiles`.
  * __initf__: En "initialiseringsfunktion", som skal køres inden modellen startes. Funktionen skal tage ét `Model`-objekt som argument. Modellen genererer automatisk en knap markeret "setup", som kører denne funktion.
  * __rf__: En "renderingsfunktion", som tegner agenterne. Funktionen skal tage ét sæt af `Agent`-objekter som argument. For korrekt at rendere agenterne, skal `Model.render` kaldes i den globale `draw` funktion.

For enkelthedens skyld er visse egenskaber for modellen fastsatte. Området, der viser agenterne, er altid 400x400 pixels, og vises til venstre på skærmen. Området med knapper er også 400x400 pixels, og vises til højre. Derfor _skal_ størrelsen på vinduet altid defineres til at være 800x400 i `setup` funktionen (ved brug af `size`).

Modellen sættes op således:

```python
model_42 = ag.Model(100, 20, initialize, rendering)

def setup():
    global model_42
    size(800,400)

def draw():
    global model_42
    modello.render()
```

Hvor `initialize` og `rendering` er hhv. initialiseringsfunktionen og renderingsfunktionen, defineret andetsteds.

`Model` har følgende public fields:

  * __width__: Bredden af agent-området for modellen i pixels. Denne er altid 400.
  * __height__: Højden af agent-området for modellen i pixels. Denne er altid 400.
  * __agents__: Sættet af modellens `Agent`s.
  * __tiles__: Et todimensionelt array over modellens `Tile`s.
  * __globals__: En _dictionary_, som indeholder brugerdefinerede variabler for modellen.

`Model` har følgende public methods:

  * __reset__: "Genstarter" modellen ved at generere nye, tilfældigt placerede agenter, og køre initialiseringsfunktionen.
  * __render__: Renderer alle `Agent`s, `Tile`s og knapper. Her køres også logikken for alle de knapper, der er aktive.