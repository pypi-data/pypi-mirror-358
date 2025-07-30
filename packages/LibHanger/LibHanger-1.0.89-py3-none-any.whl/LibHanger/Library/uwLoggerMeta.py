import threading
import inspect
import LibHanger.Library.uwLogger as Logger

# ネストの深さをスレッドローカルで管理
thread_local = threading.local()
thread_local.depth = 0

class LoggingMeta(type):
    
    """
    ログ出力メタクラス
    """
    
    def __new__(cls, name, bases, class_dict):
        
        """
        ファクトリメソッド
        """

        for attr_name, attr_value in class_dict.items():
            if callable(attr_value):
                class_dict[attr_name] = cls.wrap_method(attr_name, attr_value)
        return super().__new__(cls, name, bases, class_dict)
    
    @staticmethod
    def wrap_method(method_name, method):
        
        """
        メソッドをラップするデコレーター
        
        Parameters
        ----------
        method_name : Any
            メソッド名
        method : Any
            ラップするメソッド
            
        """
        
        def wrapper(*args, **kwargs):
            
            """
            メソッドの開始と終了をログに出力するラッパー
            """
            
            if not hasattr(thread_local, 'depth'):
                thread_local.dppth = 0
            
            # ネストレベルを上げる
            thread_local.depth += 1
            Logger.setDepth(thread_local.depth)
            
            # 引数の出力
            sig = inspect.signature(method)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            args_repr = ''
            if bound_args:
                args_repr = ", ".join(f"{key}:{value}" for key, value in bound_args.arguments.items() if key != "self")

            # 戻り値変数初期化
            ret = None

            try:
            
                # 開始ログの出力
                Logger.startMethod(method_name, args_repr)
                
                # 関数本体の実行
                ret = method(*args, **kwargs)
                                
            except Exception as e:
                
                # エラーメッセージの出力
                Logger.error(method_name, e)

                # 例外スロー
                raise

            finally:
                
                # 終了ログの出力
                Logger.endMethod(method_name, ret)
                
                # ネストレベルを戻す
                thread_local.depth -= 1
                Logger.setDepth(thread_local.depth)

            return ret
        return wrapper