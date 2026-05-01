Step 4 - Retrieval baseline
A simple retriever:
- keyword / BM25/ TF-IDF style baseline
- top-k evidence selection
- weak-evidence refusal

The first retrieval baseline in the cleanest possible way:
1. turn chunks into searchable text
2. score chunks against the question with a simple baseline
3. return top-k evidence
4. refuse when evidence is weak 

We want a retriever to answer:
- Which chunks are most relevant to the user question?
- What are the top k pieces of evidence?
- Should we refuse because the evidence is too weak?

Pipeline: user question -> Vectorize q + chunks with TF-IDF -> Compute similarity scores -> Sort chunks by score
    -> Take top-k chunks -> If best score is too low: refuse; else: pass evidence to answer generator

Why TF-IDF first: Bcz it gives you a good baseline with low complexity. 
- It's easy to explain | easy to debug | fast | a strong benchmark before embeddings

Structure
rag/ retrieve_tfidf.py | retrieval_schema.py | test_retrieval.py
kb/ processed/ chunks.json

What each file does
- retrieval_schema.py - Defines the output structure for retrieved chunks
- retrieve_tfidf.py - Retrieval logic: load chunks | build TF-IDF matrix | score query | return top-k | refusal check
- test_retrieval.py - Let's you test question quickly from terminal

How the retrieval works
0. Let's say the user asks: Can I take this medicine with food?
- The retriever does this:
1. Convert every chunk into TF-IDF features - each chunk becomes a vector
2. Convert the quer into the same feature space - Now the query is also a vector
3. Measure similarity - We compare the query vector to each chunk vector using cosine similarity (higher is better)
4. Sort by score - Highest first
5. Keep top-k 
6. Weak-evidence refusal - If the best score is to low, we say: no enough evidence | can't answer confidently 

Why weak-evidence refusal matters
In a medical system, you do not want the chatbot to confidently invent an answer just bcz the user asked sth. 
So this rule is essential: if best_score < threshold => refuse
threshold: too low -> chatbot answers from weak evidence | too high -> chatbot refuses too often

Summary: For now the bot only: find relevent chunks -> score them -> return evidence -> signal weak evidence

Next step: 
- Connect retrieval to your answer layer
- If should_refuse = True, return safe refusal
- Otherwise pass top chunks into answer generation


==========================================
BM25
Idea
- TF-IDF uses TfidfVectorizer
- BM25 uses tokenized text + BM25 scoring
Now, the TF-IDF retriever does: query+chunks -> vectorize -> score similarit ->rank top-k -> weak-evidence refusal
If add BM25, the pipeline: query+chunks -> tokenize text -> BM25 scores -> rank top-k -> weak-evidence refusal

Design
- Keep the current TF-IDF retriever
- add a new file for BM25
- make both return the same RetrievalResult format
Later test: TF-IDF | BM25 | semantic retrieval - and compare them easily. 

How BM25 works
BM25 is a stronger keyword-based retriever than plain TF-IDF in many search settings. 
It rewards chunks that:
- contain the query terms | contain them multiple times | are not too long | contain rarer, more informative words

Code
- TF-IDF
vectorizer.fit_transform(texts)
query_vector = vectorizer.transform([query])
scores = cosine_similarity(query_vector, chunk_matrix)

- BM25
tokenized_chunks = [text.split() for text in texts]
bm25 = BM25Okapi(tokenized_chunks)
tokenized_query = query.split()
scores = bm25.get_scores(tokenized_query)

BM25 works on token lists, not vector matrices. 

Disadvantage of BM25
It's a better lexical baseline, but still not semantic retrieval
eg. query: "high temperature" | chunk: "fever"
It would miss the match. 
Solution: embedding

Pipeline
1. Keep TF-IDF - good for first baseline
2. Add BM25 in a separate file - Best lexical baseline comparison
3. Evaluate both - check: top-k relevance | refusal behavior | common failture cases
4. Later add embeddings - semantic retriever

Why the threshold differnt?
In TF-IDF cosine similarity, scores are often in a range like: 0 to 1
But BM25 scores are not normalized the same way. 
For BM25, ou need to test real queries and tune separately. 
A placeholder: refusal_threshold=1.0 # It's noly a starting point.

Tokenization - later improve:
- stopword removal
- stemming or lemmatization
- preserving medical terms carefully

Summary
To add BM25, keep the same retrieval pipeline, create a new retriever file, tokenize chunk text score with BM25Okapi, return the same RetrievalResult format, and tune a separate refusal threshold. 




