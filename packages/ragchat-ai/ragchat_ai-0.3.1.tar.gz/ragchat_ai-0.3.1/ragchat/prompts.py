from typing import Tuple

from ragchat.definitions import (
    Example,
    Flow,
    Language,
    Prompt,
    SemanticType,
    Translations,
)

_is = Translations(en="is", es="es", fr="est", de="ist")
_is_not = Translations(en="is not", es="no es", fr="n'est pas", de="ist nicht")
_facts = Translations(en="facts", es="hechos", fr="faits", de="Fakten")
_fact = Translations(en="fact", es="hecho", fr="fait", de="Fakt")
_summary = Translations(en="summary", es="resumen", fr="sommaire", de="Zusammenfassung")

SEMANTIC_WORDS = {
    SemanticType.RECENT: [
        "recent",
        "new",
        "current",
        "fresh",
        "latest",
        "lately",
        "modern",
        "up-to-date",
        "contemporary",
        "today",
        "novel",
        "just",
        "now",
        "trending",
        "present",
        "newly",
        "emerging",
        "cutting-edge",
        "updated",
    ],
    SemanticType.OLD: [
        "old",
        "first time",
        "outdated",
        "past",
        "former",
        "historic",
        "ancient",
        "vintage",
        "previous",
        "obsolete",
        "bygone",
        "earlier",
        "dated",
        "traditional",
        "antiquated",
        "prior",
        "archaic",
        "once",
        "long-ago",
        "yesteryear",
    ],
}


SUMMARY_FACTS = Prompt(
    prompt_type="system",
    prompt=Translations(
        en=f"""
Extract a one-line summary and concise facts with format:
## {_summary.get(Language.ENGLISH).capitalize()}
[{_summary.get(Language.ENGLISH).capitalize()}]

## {_facts.get(Language.ENGLISH).capitalize()}
- [{_fact.get(Language.ENGLISH).capitalize()}]
""",
        es=f"""
Extrae un resumen de una línea y hechos concisos con el formato:
## {_summary.get(Language.SPANISH).capitalize()}
[{_summary.get(Language.SPANISH).capitalize()}]

## {_facts.get(Language.SPANISH).capitalize()}
- [{_fact.get(Language.SPANISH).capitalize()}]
""",
        fr=f"""
Extrayez un sommarie d'une ligne et des faits concis avec le format :
## {_summary.get(Language.FRENCH).capitalize()}
[{_summary.get(Language.FRENCH).capitalize()}]

## {_facts.get(Language.FRENCH).capitalize()}
- [{_fact.get(Language.FRENCH).capitalize()}]
""",
        de=f"""
Extrahieren Sie eine einzeilige Zusammenfassung und prägnante Fakten im Format:
## {_summary.get(Language.GERMAN).capitalize()}
[{_summary.get(Language.GERMAN).capitalize()}]

## {_facts.get(Language.GERMAN).capitalize()}
- [{_fact.get(Language.GERMAN).capitalize()}]
""",
    ),
    examples=[],
)

RETRIEVAL_CHAT = Prompt(
    prompt_type="system",
    prompt=Translations(
        en="""
You are a helpful assistant. Memories are your own recollections. Use only relevant memories to inform your responses.
""",
        es="""
Eres un asistente útil. Los recuerdos son tus propias rememoraciones. Utiliza solo recuerdos relevantes para informar tus respuestas.
""",
        fr="""
Vous êtes un assistant utile. Les souvenirs sont vos propres souvenirs. Utilisez uniquement les souvenirs pertinents pour éclairer vos réponses.
""",
        de="""
Sie sind ein hilfreicher Assistent. Erinnerungen sind Ihre eigenen Erinnerungen. Verwenden Sie nur relevante Erinnerungen, um Ihre Antworten zu informieren.
""",
    ),
    examples=[],
)

RETRIEVAL_RAG = Prompt(
    prompt_type="user",
    prompt=Translations(
        en="""
Task: Respond to the user query using the provided sources.

Instructions:
- Use only relevant sources to infer the answer
- Incorporate inline citations in brackets: [id]
- Citation ids must correspond to the ids in the source tags `<source id=*>`
- If uncertain, concisely ask the user to rephrase the question to see if you can get better sources
""",
        es="""
Tarea: Responder a la consulta del usuario utilizando las fuentes proporcionadas.

Instrucciones:
- Utiliza solo fuentes relevantes para informar tus respuestas
- Incorpora citas en línea entre corchetes: [id]
- Los ids de las citas deben corresponder a los ids en las etiquetas de fuente `<source id=*>`
- Si no estás seguro, pide concisamente al usuario que reformule la pregunta para ver si puedes obtener mejores fuentes
""",
        fr="""
Tâche : Répondre à la requête de l'utilisateur en utilisant les sources fournies.

Instructions :
- Utilisez uniquement les sources pertinentes pour éclairer vos réponses
- Intégrez des citations en ligne entre crochets : [id]
- Les identifiants de citation doivent correspondre aux identifiants dans les balises source `<source id=*>`
- En cas d'incertitude, demandez de manière concise à l'utilisateur de reformuler la question pour voir si vous pouvez obtenir de meilleures sources
""",
        de="""
Aufgabe: Beantworten Sie die Benutzeranfrage anhand der bereitgestellten Quellen.

Anweisungen:
- Verwenden Sie nur relevante Quellen, um Ihre Antworten zu gestalten
- Fügen Sie Inline-Zitate in Klammern ein: [id]
- Die Zitat-IDs müssen mit den IDs in den Quell-Tags `<source id=*>` übereinstimmen
- Wenn Sie unsicher sind, bitten Sie den Benutzer prägnant, die Frage neu zu formulieren, um zu sehen, ob Sie bessere Quellen erhalten können
""",
    ),
    examples=[
        Example(
            flow=Flow.FILE,
            example_input=Translations(
                en="""
<query>
What were the findings of the study on kv cache?
</query>

<source id="1">
Instead of predicting one token at a time, DeepSeek employs MTP, allowing the model to predict multiple future tokens in a single step.
6</source>
<source id="2">
Red Hat's blog post on integrating DeepSeek models with vLLM 0.7.1 highlights that MLA offers up to 9.6x more memory capacity for key-value (KV) caches.
11</source>
""",
                es="""
<query>
¿Cuáles fueron los hallazgos del estudio sobre la caché KV?
</query>

<source id="1">
En lugar de predecir un token a la vez, DeepSeek emplea MTP, lo que permite al modelo predecir múltiples tokens futuros en un solo paso.
6</source>
<source id="2">
La publicación del blog de Red Hat sobre la integración de los modelos DeepSeek con vLLM 0.7.1 destaca que MLA ofrece hasta 9,6 veces más capacidad de memoria para las cachés de clave-valor (KV).
11</source>
""",
                fr="""
<query>
Quelles ont été les conclusions de l'étude sur le cache KV ?
</query>

<source id="1">
Au lieu de prédire un token à la fois, DeepSeek utilise MTP, permettant au modèle de prédire plusieurs tokens futurs en une seule étape.
6</source>
<source id="2">
L'article de blog de Red Hat sur l'intégration des modèles DeepSeek avec vLLM 0.7.1 souligne que MLA offre jusqu'à 9,6 fois plus de capacité mémoire pour les caches clé-valeur (KV).
11</source>
""",
                de="""
<query>
Was waren die Ergebnisse der Studie zum KV-Cache?
</query>

<source id="1">
Anstatt ein Token nach dem anderen vorherzusagen, verwendet DeepSeek MTP, wodurch das Modell mehrere zukünftige Tokens in einem einzigen Schritt vorhersagen kann.
6</source>
<source id="2">
Der Blogbeitrag von Red Hat zur Integration von DeepSeek-Modellen mit vLLM 0.7.1 hebt hervor, dass MLA bis zu 9,6x mehr Speicherkapazität für Key-Value (KV)-Caches bietet.
11</source>
""",
            ),
            example_output=Translations(
                en="""
According to Red Hat's blog post on integrating DeepSeek models, MLA offers up to 9.6x more memory capacity for key-value caches [2].
""",
                es="""
Según la publicación del blog de Red Hat sobre la integración de modelos DeepSeek, MLA ofrece hasta 9,6 veces más capacidad de memoria para cachés de clave-valor [2].
""",
                fr="""
Selon l'article de blog de Red Hat sur l'intégration des modèles DeepSeek, MLA offre jusqu'à 9,6 fois plus de capacité mémoire pour les caches clé-valeur [2].
""",
                de="""
Laut dem Blogbeitrag von Red Hat zur Integration von DeepSeek-Modellen bietet MLA bis zu 9,6-mal mehr Speicherkapazität für Schlüssel-Wert-Caches [2].
""",
            ),
        ),
    ],
)


MSG_CLASSIFICATION = Prompt(
    prompt_type="system",
    prompt=Translations(
        en="""
Task: Classify the INPUT as 'statement', 'question', 'none'.

Definitions:
- statement: A declaration, assertion or instruction.
- question: An interrogative message seeking information.
- none: The input is incoherent, empty or does not fit into any category.

Instructions:
- Don't answer questions or provide explanations, just classify the message.
- Write 'statement' or 'question' or 'none'
""",
        es="""
Tarea: Clasifica la ENTRADA como 'statement', 'question' o 'none'.

Definiciones:
- statement: Una declaración, afirmación o instrucción.
- question: Un mensaje interrogativo que busca información.
- none: La entrada es incoherente, está vacía o no encaja en ninguna categoría.

Instrucciones:
- No respondas preguntas ni des explicaciones, solo clasifica el mensaje.
- Escribe 'statement' o 'question' o 'none'
""",
        fr="""
Tâche : Classifier l'ENTRÉE comme 'statement', 'question' ou 'none'.

Définitions :
- statement : Une déclaration, une affirmation ou une instruction.
- question : Un message interrogatif cherchant à obtenir des informations.
- none : L'entrée est incohérente, vide ou ne correspond à aucune catégorie.

Instructions :
- Ne répondez pas aux questions et ne donnez pas d'explications, classez simplement le message.
- Écrivez 'statement', 'question' ou 'none'
""",
        de="""
Aufgabe: Klassifiziere die EINGABE als 'statement', 'question' oder 'none'.

Definitionen:
- statement: Eine Aussage, Behauptung oder Anweisung.
- question: Eine Frage, die nach Informationen sucht.
- none: Die Eingabe ist unzusammenhängend, leer oder passt in keine Kategorie.

Anweisungen:
- Beantworte keine Fragen und gib keine Erklärungen, sondern klassifiziere nur die Nachricht.
- Schreibe 'statement', 'question' oder 'none'
""",
    ),
    examples=[
        Example(
            flow=Flow.CHAT,
            example_input=Translations(
                en="""Is it true that the Kingdom of Italy was proclaimed in 1861, while the French Third Republic was established in 1870 and therefore Italy is technically older?""",
                es="""¿Es cierto que el Reino de Italia fue proclamado en 1861, mientras que la Tercera República Francesa se estableció en 1870 y por lo tanto Italia es técnicamente más antigua?""",
                fr=""""Est-il vrai que le Royaume d'Italie a été proclamé en 1861, tandis que la Troisième République française a été établie en 1870 et que l'Italie est donc techniquement plus ancienne?""",
                de="""Stimmt es, dass das Königreich Italien 1861 ausgerufen wurde, während die Dritte Französische Republik 1870 gegründet wurde und Italien somit technisch älter ist?""",
            ),
            example_output=Translations(
                en="question",
                es="question",
                fr="question",
                de="question",
            ),
        ),
        Example(
            flow=Flow.CHAT,
            example_input=Translations(
                en="""Paris is the capital of France. Rome is the capital of Italy.""",
                es="""París es la capital de Francia. Roma es la capital de Italia.""",
                fr=""""Paris est la capitale de la France. Rome est la capitale de l'Italie.""",
                de="""Paris ist die Hauptstadt Frankreichs. Rom ist die Hauptstadt Italiens.""",
            ),
            example_output=Translations(
                en="statement",
                es="statement",
                fr="statement",
                de="statement",
            ),
        ),
        Example(
            flow=Flow.CHAT,
            example_input=Translations(
                en="""Florp wizzlebop cronkulated the splonk! Zizzleflap {}[]()<>:;"/|,.<>? drumblesquanch, but only if the quibberflitz jibberflops. Blorp???""",
                es="""¡Florp wizzlebop cronkuleó el splonk! ¡Zizzleflap {}[]()<>:;"/|,.<>? drumblecuancha, pero solo si el quibberflitz jibberflops! ¡Blorp???""",
                fr="""Florp wizzlebop a cronkulé le splonk ! Zizzleflap {}[]()<>:;"/|,.<>? drumblecuancha, mais seulement si le quibberflitz jibberflops. Blorp ???""",
                de="""Florp wizzlebop hat den Splonk cronkuliert! Zizzleflap {}[]()<>:;"/|,.<>? drumblecuancha, aber nur wenn der quibberflitz jibberflops. Blorp???""",
            ),
            example_output=Translations(
                en="none",
                es="none",
                fr="none",
                de="none",
            ),
        ),
    ],
)


### FORMAT ###

FORMAT = Prompt(
    prompt_type="system",
    prompt=Translations(
        en="""
""",
        es="""
""",
        fr="""
""",
        de="""
""",
    ),
    examples=[
        Example(
            flow=Flow.CHAT,
            example_input=Translations(
                en="""
""",
                es="""
""",
                fr="""
""",
                de="""
""",
            ),
            example_output=Translations(
                en="""
""",
                es="""
""",
                fr="""
""",
                de="""
""",
            ),
        ),
        Example(
            flow=Flow.FILE,
            example_input=Translations(
                en="""
""",
                es="""
""",
                fr="""
""",
                de="""
""",
            ),
            example_output=Translations(
                en="""
""",
                es="""
""",
                fr="""
""",
                de="""
""",
            ),
        ),
    ],
)


def get_equivalence(e1: str, e2: str, lan: Language) -> Tuple[str, str]:
    is_str = _is.get(lan)
    is_not_str = _is_not.get(lan)

    positive_equivalence = f"{e1} {is_str} {e2}"
    negative_equivalence = f"{e1} {is_not_str} {e2}"

    return (positive_equivalence, negative_equivalence)
