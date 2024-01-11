#(+ % b)

(defn add [a b] (+ a b))

(def add (fn [a b] (+ a b)))

(defn- private-add [a b] (+ a b))

(defmacro square [x] `(* ~x ~x))

(defmethod shape-area :circle [{:keys [radius]}] (* Math/PI (* radius radius)))
