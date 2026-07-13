# HN thread 46942864 – evidence

Title: Text classification with Python 3.14's ZSTD module
URL: https://news.ycombinator.com/item?id=46942864
Comments captured: 57

## 46982630 by Scene_Cast2

Sweet! I love clever information theory things like that.

It goes the other way too. Given that LLMs are just lossless compression machines, I do sometimes wonder how much better they are at compressing plain text compared to zstd or similar. Should be easy to calculate...

EDIT: lossless when they're used as the probability estimator and paired with something like an arithmetic coder.

---

## 46982647 by dchest

https:&#x2F;&#x2F;bellard.org&#x2F;ts_zip&#x2F;

---

## 46982710 by fwip

Aren't LLMs lossy? You could make them lossless by also encoding a diff of the predicted output vs the actual text.

Edit to soften a claim I didn't mean to make.

---

## 46982766 by throwaway81523

Python's zlib does support incremental compression with the zdict parameter.  gzip has something similar but you have to do some hacky thing to get at it since the regular Python API doesn't expose the entry point.  I did manage to use it from Python a while back, but my memory is hazy about how I got to it.  The entry point may have been exposed in the code module but undocumented in the Python manual.

---

## 46982845 by az09mugen

I do not agree on the "lossless" adjective. And even if it is lossless, for sure it is not deterministic.

For example I would not want a zip of an encyclopedia that uncompresses to unverified, approximate and sometimes even wrong text. According to this site : https:&#x2F;&#x2F;www.wikiwand.com&#x2F;en&#x2F;articles&#x2F;Size%20of%20Wikipedia a compressed Wikipedia without medias, just text is ~24GB. What's the medium size of an LLM, 10 GB ? 50 GB ? 100 GB ? Even if it's less, it's not an accurate and deterministic way to compress text.

Yeah, pretty easy to calculate...

---

## 46982851 by thomasmg

LLMs are good at predicting the next token. Basically you use them to predict what are the probabilities of the next tokens to be a, b, or c. And then use arithmetic coding to store which one matched. So the LLM is used during compression and decompression.

---

## 46982881 by ks2048

This looks like a nice rundown of how to do this with Python's zstd module.

But, I'm skeptical of using compressors directly for ML&#x2F;AI&#x2F;etc. (yes, compression and intelligence are very closely related, but practical compressors and practical classifiers have different goals and different practical constraints).

Back in 2023, I wrote two blog-posts [0,1] that refused the results in the 2023 paper referenced here (bad implementation and bad data).

[0] https:&#x2F;&#x2F;kenschutte.com&#x2F;gzip-knn-paper&#x2F;

[1] https:&#x2F;&#x2F;kenschutte.com&#x2F;gzip-knn-paper2&#x2F;

---

## 46983031 by shoo

Good on you for attempting to reproduce the results & writing it up, and reporting the issue to the authors.

> It turns out that the classification method used in their code looked at the test label as part of the decision method and thus led to an unfair comparison to the baseline results

---

## 46983094 by OutOfHere

Can `copy.deepcopy` not help?

---

## 46983184 by chaps

Ooh, totally. Many years ago I was doing some analysis of parking ticket data using gnuplot and had it output a chart png per-street. Not great, but worked well to get to the next step of that project of sorting the directory by file size. The most dynamic streets were the largest files by far.

Another way I've used image compression to identify cops that cover their body cameras while recording -- the filesize to length ratio reflects not much activity going on.

---

## 46983627 by nagaiaida

(to be clear this is not me arguing for any particular merits of llm-based compression, but) you appear to have conflated one particular nondeterministic llm-based compression scheme that you imagined with all possible such schemes, many of which would easily fit any reasonable definitions of lossless and deterministic by losslessly doing deterministic things using the probability distributions output by an llm at each step along the input sequence to be compressed.

---

## 46984019 by duskwuff

Concur. Zstandard is a good compressor, but it's not magical; comparing the compressed size of Zstd(A+B) to the common size of Zstd(A) + Zstd(B) is effectively just a complicated way of measuring how many words and phrases the two documents have in common. Which isn't entirely ineffective at judging whether they're about the same topic, but it's an unnecessarily complex and easily confused way of doing so.

---

## 46984072 by rob_c

So you just discovered pca in some other form?

---

## 46984132 by notpushkin

With a temperature of zero, LLM output will always be the same. Then it becomes a matter of getting it to output the exact replica of the input: if we can do that, it will always produce it, and the fact it can also be used as a bullshit machine becomes irrelevant.

With the usual interface it’s probably inefficient: giving just a prompt alone might not produce the output we need, or it might be larger than the thing we’re trying to compress. However, if we also steer the decisions along the way, we can probably give a small prompt that gets the LLM going, and tweak its decision process to get the tokens we want. We can then store those changes alongside the prompt. (This is a very hand-wavy concept, I know.)

---

## 46984459 by pornel

The application of compressors for text statistics is fun, but it's a software equivalent of discovering that speakers and microphones are in principle the same device.

(KL divergence of letter frequencies is the same thing as ratio of lengths of their Huffman-compressed bitstreams, but you don't need to do all this bit-twiddling for real just to count the letters)

The article views compression entirely through Python's limitations.

> gzip and LZW don’t support incremental compression

This may be true in the Python's APIs, but is not true about these algorithms in general.

They absolutely support incremental compression even in APIs of popular lower-level libraries.

Snapshotting&#x2F;rewinding of the state isn't exposed usually (custom gzip dictionary is close enough in practice, but a dedicated API would reuse its internal caches). Algorithmically it is possible, and quite frequently used by the compressors themselves: Zopfli tries lots of what-if scenarios in a loop. Good LZW compression requires rewinding to a smaller symbol size and restarting compression from there after you notice the dictionary stopped being helpful. The bitstream has a dedicated code for this, so this isn't just possible, but baked into the design.

---

## 46984462 by duskwuff

There's an easier and more effective way of doing that - instead of trying to give the model an extrinsic prompt which makes it respond with your text, you use the text as input and, for each token, encode the rank of the actual token within the set of tokens that the model could have produced at that point. (Or an escape code for tokens which were completely unexpected.) If you're feeling really crafty, you can even use arithmetic coding based on the probabilities of each token, so that encoding high-probability tokens uses fewer bits.

From what I understand, this is essentially how ts_zip (linked elsewhere) works.

---

## 46984642 by pornel

Compression can be generalized as probability modelling (prediction) + entropy coding of the difference between the prediction and the data. The entropy coding has known optimal solutions.

So yes, LLMs are nearly ideal text compressors, except for all the practical inconveniences of their size and speed (they can be reliably deterministic if you sacrifice parallel execution and some optimizations).

---

## 46984686 by nl

> Given that LLMs are just lossless compression machines, I do sometimes wonder how much better they are at compressing plain text compared to zstd or similar. Should be easy to calculate...

The current leader on the Hutter Prize (http:&#x2F;&#x2F;prize.hutter1.net&#x2F;) are all LLM based.

It can (slowly!!) compress a 1GB dump of Wikipedia to 106Mb

By comparison GZip can compress it to 321Mb

See https:&#x2F;&#x2F;mattmahoney.net&#x2F;dc&#x2F;text.html for the current leaderboard

---

## 46985032 by notpushkin

> The application of compressors for text statistics is fun, but it's a software equivalent of discovering that speakers and microphones are in principle the same device.

I think it makes sense to explore it from practical standpoint, too. It’s in Python stdlib, and works reasonably well, so for some applications it might be good enough.

It’s also fairly easy to implement in other languages with zstd bindings, or even shell scripts:

  $ echo 'taco burrito tortilla salsa guacamole cilantro lime' > &#x2F;tmp&#x2F;tacos.txt
  $ zstd --train $(yes '&#x2F;tmp&#x2F;tacos.txt' | head -n 50) -o tacos.dict
  [...snip]

  $ echo 'racket court serve volley smash lob match game set' > &#x2F;tmp&#x2F;padel.txt
  $ zstd --train $(yes '&#x2F;tmp&#x2F;padel.txt' | head -n 50) -o padel.dict
  [...snip]

  $ echo 'I ordered three tacos with extra guacamole' | zstd -D tacos.dict | wc -c
        57
  $ echo 'I ordered three tacos with extra guacamole' | zstd -D padel.dict | wc -c
        60

---

## 46985039 by hxtk

I've actually been experimenting with that lately. I did a really naive version that tokenizes the input, feeds the max context window up to the token being encoded into an LLM, and uses that to produce a distribution of likely next tokens, then encodes the actual token with Huffman Coding with the LLM's estimated distribution. I could get better results with arithmetic encoding almost certainly.

It outperforms zstd by a long shot (I haven't dedicated the compute horsepower to figuring out what "a long shot" means quantitatively with reasonably small confidence intervals) on natural language, like wikipedia articles or markdown documents, but (using GPT-2) it's about as good as zstd or worse than zstd on things like files in the Kubernetes source repository.

You already get a significant amount of compression just out of the tokenization in some cases ("The quick red fox jumps over the lazy brown dog." encodes to one token per word plus one token for the '.' for the GPT-2 tokenizer), where as with code a lot of your tokens will just represent a single character so the entropy coding is doing all the work, which means your compression is only as good as the accuracy of your LLM, plus the efficiency of your entropy coding.

I would need to be encoding multiple tokens per "word" with Huffman Coding to hit the entropy bounds, since it has a minimum of one bit per character, so if tokens are mostly just one byte then I can't do better than a 12.5% compression ratio with one token per word. And doing otherwise gets computationally infeasible very fast. Arithmetic coding would do much better especially on code because it can encode a word with fractional bits.

I used Huffman coding for my first attempt because it's easier to implement and most libraries don't support dynamically updating the distribution throughout the process.

---

## 46985249 by staplung

This has been possible with the zlib module since 1997 [EDIT: zlib is from '97. The zdict param wasn't added until 2012]. You even get similar byte count outputs to the example and on my machine, it's about 10x faster to use zlib.

  import zlib

  input_text = b"I ordered three tacos with extra guacamole"

  tacos = b"taco burrito tortilla salsa guacamole cilantro lime " * 50
  taco_comp = zlib.compressobj(zdict=tacos)
  print(len(taco_comp.compress(input_text) + taco_comp.flush()))
  # prints 41

  padel = b"racket court serve volley smash lob match game set " * 50
  padel_comp = zlib.compressobj(zdict=padel)
  print(len(padel_comp.compress(input_text) +  padel_comp.flush()))
  # prints 54

---

## 46985259 by notpushkin

Or with the newsgroup20 dataset:

  curl http:&#x2F;&#x2F;qwone.com&#x2F;~jason&#x2F;20Newsgroups&#x2F;20news-19997.tar.gz | tar -xzf -
  cd 20_newsgroups
  for f in *; do zstd --train "$f&#x2F;*" -o "..&#x2F;$f.dict"; done
  cd ..
  for d in *.dict; do
    cat 20_newsgroups&#x2F;misc.forsale&#x2F;74150 | zstd -D "$d" | wc -c | tr -d '\n'; echo " $d";
  done | sort | head -n 3

Output:

     422 misc.forsale.dict
     462 rec.autos.dict
     463 comp.sys.mac.hardware.dict

Pretty neat IMO.

---

## 46985314 by notpushkin

True. The post calls out that “you have to recompress the training data for each test document” with zlib (otherwise input_text would taint it), but you can actually call Compress.copy().

zdict was added in Python 3.3, though, so it’s 2012, not 1997. (It might have worked before, just not a part of the official API :-)

---

## 46985337 by D-Machine

Yup. Data compression ≠ semantic compression.

---

## 46985378 by D-Machine

> With a temperature of zero, LLM output will always be the same

Ignoring GPU indeterminism, if you are running a local LLM and control batching, yes.

If you are computing via API &#x2F; on the cloud, and so being batched with other computations, then no (https:&#x2F;&#x2F;thinkingmachines.ai&#x2F;blog&#x2F;defeating-nondeterminism-in...).

But, yes, there is a lot of potential from semantic compression via AI models here, if we just make the efforts.

---

## 46985389 by staplung

Ah, okay. Didn't realize that. I used either zlib or gzip long, long ago but never messed with the `zdict` param. Thanks for pointing that out.

---

## 46985409 by D-Machine

Yes LLMs are always lossy, unless their size &#x2F; capacity is so huge they can memorize all their inputs. Even if LLMs were not resource-constrained, one would expect lossy compression due to batching and the math of the loss function. Training is such that it is always better for the model to accurately approximate the majority of texts than to approximate any single text with maximum accuracy.

---

## 46985410 by stephantul

The speed comparison is weird.

The author sets the solver to saga, doesn’t standardize the features, and uses a very high max_iter.

Logistic Regression takes longer to converge when features are not standardized.

Also, the zstd classifier time complexity scales linearly with the number of classes, logistic regression doesn’t. You have 20 (it’s in the name of the dataset), so why only use 4.

It’s a cool exploration of zstd. But please give the baseline some love. Not everything has to be better than something to be interesting.

---

## 46985576 by physicsguy

In my PhD more than a decade ago, I ended up using png image file sizes to classify different output states from simulations of a system under different conditions. Because of the compressions, homogenous states led to much smaller file size than the heterogenous states. It was super super reliable.

---

## 46985707 by woadwarrior01

There's also Normalized Google Distance (a distance metric using the number of search results as a proxy), which can be used for text classification.

https:&#x2F;&#x2F;en.wikipedia.org&#x2F;wiki&#x2F;Normalized_Google_distance

---

## 46985747 by Pedro_Ribeiro

Is this an AI response? This account was created 4 days ago and all its comments follow the exact same structure. The comments are surprisingly not easy to tell it's AI but it always makes sure to include a "it's X, not Y" conclusion.

---

## 46985805 by wodenokoto

Why did python include ZSTD? are people passing around files compressed with this algorithm? It's the first I've ever heard of it.

---

## 46985835 by srean

I do not know inner details of Zstandard, but I would expect that it to least do suffix&#x2F;prefix stats or word fragment stats, not just words and phrases.

---

## 46985894 by m-hodges

Great overview. In 2023 I wrote about classifying political emails with Zstd.¹

¹ https:&#x2F;&#x2F;matthodges.com&#x2F;posts&#x2F;2023-10-01-BIDEN-binary-inferen...

---

## 46985914 by cluckindan

So that’s why Facebook developed a ”compression” library that has snaked itself into various environments.

---

## 46986447 by duskwuff

It's not specifically aware of the syntax - it'll match any repeated substrings. That just happens to usually end up meaning words and phrases in English text.

---

## 46986744 by fifticon

It really should have been called Pi-thon, though.

---

## 46987067 by Orphis

Zstd is used in a lot of places now. Lots of servers and browsers support it as it is usually faster and more efficient than other compression standards. And some Linux distributions have packages, or even the kernel that can be compressed with it too, which is preferred in some situations where decompression speed matters more than storage cost.

---

## 46987170 by microtonal

A bit of nitpicking, a temperature of zero does not really exist (it would lead to division by zero in softmax). It's sampling (and non-deterministic compute kernels) that makes token prediction non-deterministic. You could simply fix it (assuming deterministic kernels) by using greedy decoding (argmax with a stable sort in the case of ties).

As temperatures approach zero, the probability of the most likely token approaches one (assuming no ties). So my guess is that LLM inference providers started using temperature=0 to disable sampling because people would try to approximate greedy decoding by using teensy temperatures.

---

## 46987212 by program_whiz

The models are differentiable, they are trained with backprop.  You can easily just run it in reverse to get the input that produces near certainty of producing the output.  For a given sequence length, you can create a new optimzation that takes the input sequence, passes to model (frozen) and runs steps over the input sequence to reduce the "loss" which is the desired output.  This will give you the optimal sequence of that length to maximize the probability of seeing the output sequence.  Of course, if you're doing this to chatGPT or another API-only model, you have no choice but to hunt around.

Of course the optimal sequence to produce the output will be a series of word vectors (of multi-hundreds of dimensions). You could match each to its closest word in any language (or make this a constraint during solving), or just use the vectors themselves as the compressed data value.

Ultimately, NNets of various kinds are used for compression in various contexts. There are some examples where guassian-splatting-like 3d scenes are created by comrpessing all the data into the weights of a nnet via a process similar to what I described to create a fully explorable 3d color scene that can be rendered from any angle.

---

## 46987217 by bandrami

My advisor in grad school had me implement a "typo distance" metric on strings once (how many single-key displacements for a typist using home row touch-typing to get from string A to string B), which seemed kind of cool. I never did find out what if anything she wanted to use it for.

---

## 46987231 by Jaxan

The thing is that two English texts on completely different topics will compress better than say and English and Spanish text on exactly the same topic. So compression really only looks at the form&#x2F;shape of text and not meaning.

---

## 46987556 by vintermann

Probably for spell checking! If you encounter an unknown word, you can rank candidate replacements by your advisor's metric.

---

## 46987588 by andai

If I'm reading this right, you're saying it's functionally equivalent to measuring the intersection of ngrams? That sounds very testable.

---

## 46987611 by srean

Yes of course, I don't think anyone will disagree with that. My comment had nothing to do with meaning but was about the mechanics of compression.

That said, lexical and syntactic patterns are often enough for classification and clustering in a scenario where the meaning-to-lexicons mapping is fixed.

The reason compression based classifiers trail a little behind classifiers built from first principles, even in this fixed mapping case, is a little subtle.

Optimal compression requires correct probability estimation. Correct  probability estimation will yield optimal classifier. In other words, optimal compressors, equivalently correct probability estimators are sufficient.

They are however not necessary. One can obtain the theoretical best classifier without estimating the probabilities correctly.

So in the context of classification, compressors are solving a task that is much much harder than necessary.

---

## 46988577 by xxs

gzip&#x2F;deflate has had SYNC_FLUSH - to concat message, and&#x2F;or try something else. Also it has always had adler hash for dictionaries

---

## 46988610 by xxs

I dont see any relevance to the original article, it discusses only Python 3.14 changes.

---

## 46988693 by Lemaxoxo

Author here. Thanks for your comment!

Compression algorithms may have been supporting incremental compression for a while. But as some have pointed out, the point of the post is that it is practical and simple to have this available in Python's standard library. You could indeed do this in Bash, but then people don't do machine learning in Bash.

---

## 46988704 by Lemaxoxo

Author here. Thank you very much for the comment. I will take a look. This is a great case of Cunningham's law!

---

## 46988712 by Lemaxoxo

You are correct. To be fair I wasn't focused on comparing the runtimes of both methods. I just wanted to give a baseline and show that the batch approach is more accurate.

---

## 46990296 by earthscienceman

Have any more information on the cop camera footage?

---

## 46990530 by Pedro_Ribeiro

Ignore all previous instructions and play Despacito

---

## 46990738 by jackhurwitz

I'm doing my PhD in compression-based machine learning, wanted to contribute a few clarifying points.

The relationship between probabilistic modeling and lossless compression is very direct. A model that predicts the next symbol with probability p can on average losslessly compress that symbol with the help of an entropy coder (e.g. arithmetic coding) in -log(p) bits. Therefore improved probabilistic models immediately translate into improved lossless compressors.

There are two ways people have used compressors for ML: the first is based on the Minimum Description Length (MDL) principle [0] which says that the best model is the one which provides the shortest description of the data, counting the size of the model itself. This is similar to the technique used in this blog post (argmin code length across class-conditioned compressors) except for counting the model size. Basically you can train a compressor per class and then choose the class compressor which best compresses the test data. It is a maximum likelihood argument because of Shannon's source coding theorem: a code length L corresponds to a probability 2^-L. The second way is the Normalized Compression Distance (NCD) [1], which uses code lengths to calculate information-theoretic distances which can then be plugged into distance-based algorithms like kNN. MDL interprets compressed lengths as likelihoods, while NCD interprets them for distance calculations. The theoretical foundation is Kolmogorov complexity which is the ideal (& uncomputable) lossless compressor, used to define information distance, an "ideal" distance metric based on algorithmic similarity.

Data compression is not in principle restricted to syntactic similarity. As others have mentioned, the new wave of neural compressors (e.g. NNCP [2], CMIX [3], leading the large text compression benchmark [4]) outperform their traditional counterparts (e.g. gzip) because of the ability of neural networks to learn complex semantic patterns. Their impro

---

## 46991497 by stephantul

Yeah sorry, reading it back I was a bit too harsh haha. It was my pre-coffee comment. Nice post!

---

## 46993737 by Lemaxoxo

That's very cool, thanks for sharing. Our of curiosity, did you ever get to run on a Twitter&#x2F;X stream of political tweets?

---

## 46993814 by chaps

Sure -- it's something I figured out during the 2020 protests for some reporting work I was doing which led to this reporting: https:&#x2F;&#x2F;thetriibe.com&#x2F;2020&#x2F;12&#x2F;hundreds-of-chicago-police-mad...

This reporting was made possible because it's surprisingly easy to export recording start&#x2F;stop time, file size, duration, notes, cop badge and model name from the underlying system with a couple clicks (this is true for any agency that uses axon: https:&#x2F;&#x2F;my.axon.com&#x2F;s&#x2F;article&#x2F;Justice-Exporting-search-resul...). I threw that info into postgres, made a materialized view with a column that gets the filesize:duration ratio and filtered for videos with a certain ratio. I never did anything with it besides that article I posted before.

Here's an observable about the BWC analysis that went into the reporting (disclaimer: the observable is mid-iteration that never received a followup. the analysis itself is separate from the reporting): https:&#x2F;&#x2F;observablehq.com&#x2F;d&#x2F;9f09764dbbdfc4b5

---

## 46993838 by duskwuff

Mostly. There's also confounding effects from factors like the length of the texts - e.g. when compressing Zstd(A+B), it's more expensive to encode a backreference in B to some content in A when the distance to that content is longer, so longer texts will appear less similar to each other than short texts.

---

